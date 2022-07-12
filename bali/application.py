import gzip
import inspect
import logging
import sys
from importlib import import_module
from typing import Callable

import typer
import uvicorn
from fastapi import FastAPI, Request, Response
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.routing import APIRoute
from fastapi_pagination import add_pagination
from starlette.middleware.cors import CORSMiddleware

from ._utils import singleton
from .middlewares import process_middleware
from .utils import sync_exec
from .servicer import get_servicer, make_grpc_serve

logger = logging.getLogger('bali')


class GzipRequest(Request):
    async def body(self) -> bytes:
        if not hasattr(self, "_body"):
            body = await super().body()
            if "gzip" in self.headers.getlist("Content-Encoding"):
                body = gzip.decompress(body)
            self._body = body
        return self._body


class GzipRoute(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            request = GzipRequest(request.scope, request.receive)
            return await original_route_handler(request)

        return custom_route_handler


@singleton
class Bali:
    def __init__(self, base_settings=None, **kwargs):
        self.base_settings = base_settings or {}
        self.kwargs = kwargs
        self.title = kwargs.get('title', 'Bali')

        self._app = None

        self._pb2 = None
        self._pb2_grpc = None
        self._rpc_servicer = None

        # Create FastAPI instance ref to `self._app`
        self.http()

        # Construct a ServiceServicer class ref to `self._rpc_servicer`
        self.rpc()

    def __getattribute__(self, attr, *args, **kwargs):
        try:
            return super().__getattribute__(attr)
        except AttributeError:
            return getattr(self._app, attr)

    async def __call__(self, scope, receive, send) -> None:
        await self._app.__call__(scope, receive, send)  # pragma: no cover

    @property
    def pb2(self):
        return self._pb2

    @property
    def pb2_grpc(self):
        return self._pb2_grpc

    @property
    def rpc_servicer(self):
        return self._rpc_servicer

    @staticmethod
    def _launch_http():
        uvicorn.run(
            "main:app",
            port=8000,
            reload=True,
            access_log=True,
            reload_excludes=['*.log'],
        )

    async def _launch_rpc(self):
        """Launch RPC process

        `rpc_service` is the module contains gRPC components
            (a ServiceServicer class and a serve function,
            both of them is optional).
            can be a class or function, when it's a function,
            it will be called directly.

            ServiceServicer class example:

            ```python
            class FooService(pb2_grpc.FooServiceServicer):
                def GetFoo(self, request, context):
                    schema = FooResource().get(request, context)
                    return json_format.ParseDict(schema.dict(), pb2.FooEntity())
            ```

            serve function example:

            ```python
            def serve():
                port = 9080
                server = grpc.server(
                    futures.ThreadPoolExecutor(max_workers=10),
                    interceptors=[ProcessInterceptor()],
                )
                pb2_grpc.add_FooServiceServicer_to_server(FooService(), server)
                server.add_insecure_port(f'[::]:{port}')
                server.start()
                server.wait_for_termination()
            ```

            ServiceServicer will compose with registered resources

        """
        service = self.kwargs.get('rpc_service')
        if service and service.serve:
            serve = service.serve
        else:
            serve = make_grpc_serve(self)

        # Start rpc using user defined service module
        # included sync and async mode
        if inspect.iscoroutinefunction(serve):
            await serve()
        else:
            serve()

    def _launch_event(self):
        from .events import handle
        from bali import init_handler, __version__

        event_handler = self.kwargs.get('event_handler')
        if not event_handler:
            raise Exception('event_handler not provided')
        init_handler(event_handler)
        logger.info('Bali v%s Event started.', __version__)
        while True:
            handle()

    def settings(self, **kwargs):
        self.base_settings.update(kwargs)

    def http(self):
        """load FastAPI to instance"""
        self._app = FastAPI(title='Bali', **self.base_settings)
        self._app.router.route_class = GzipRoute

        # routers
        for router in self.kwargs.get('routers', []):
            self._app.include_router(**router)
        # cors
        backend_cors_origins = self.kwargs.get('backend_cors_origins')
        if backend_cors_origins:
            self._app.add_middleware(GZipMiddleware)
            self._app.add_middleware(
                CORSMiddleware,
                allow_origins=[str(origin) for origin in backend_cors_origins],
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )
            self._app.middleware('http')(process_middleware)

        add_pagination(self._app)

    def rpc(self):
        pb2_path = f'protos.{self.title}_pb2'
        pb2_grpc_path = f'protos.{self.title}_pb2_grpc'

        try:
            self._pb2 = import_module(pb2_path)
            self._pb2_grpc = import_module(pb2_grpc_path)

            # TODO: Should support service module and service class
            service = self.kwargs.get('rpc_service')
            service_classes = [
                f'{self.title.capitalize()}Service',
                f'{self.title.capitalize()}Servicer',
            ]
            for service_class in service_classes:
                if service and hasattr(service, service_class):
                    self._rpc_servicer = getattr(service, service_class)
                    break
            else:
                self._rpc_servicer = get_servicer(self)
        except ModuleNotFoundError:
            # No module named 'protos'
            #
            # No 'protos' won't launch gRPC service,
            # but other services not affected.
            pass

    def launch(
        self,
        http: bool = False,
        rpc: bool = False,
        event: bool = False,
        shell: bool = False,
    ):
        if not any([http, rpc, event, shell]):
            typer.echo(
                'Please provided service type: '
                '--http / --rpc / --event / --shell'
            )

        if http:
            self._launch_http()

        if rpc:
            sync_exec(self._launch_rpc())

        if event:
            self._launch_event()

        if shell:
            import code
            from bali import db, __version__
            banner = (
                f"Python {sys.version} on {sys.platform}\n"
                f"App: {self.title} (Framework: Bali v{__version__})"
            )
            ctx: dict = {'db': db}
            code.interact(banner=banner, local=ctx)

    def register(self, resources_cls):
        if not isinstance(resources_cls, list):
            resources_cls = [resources_cls]

        for resource_cls in resources_cls:
            # Register HTTP service
            self._app.include_router(
                router=resource_cls.as_router(),
                prefix=resource_cls._http_endpoint,
            )
            # Register RPC service
            if self._rpc_servicer:
                resource_cls.as_servicer(self)

        add_pagination(self._app)

    def start(self):
        typer.run(self.launch)
