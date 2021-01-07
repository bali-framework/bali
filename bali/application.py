from multiprocessing import Process

import typer
import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from ._utils import singleton
from .middlewares import process_middleware


@singleton
class Bali:
    def __init__(self, base_settings=None, **kwargs):
        self.base_settings = base_settings or {}
        self.kwargs = kwargs
        self._app = None

    def __getattribute__(self, attr, *args, **kwargs):
        try:
            return super().__getattribute__(attr)
        except AttributeError:
            if not self._app:
                # uvicorn entry is __call__
                if attr == '__call__':
                    self.http()
                    return getattr(self._app, attr)

                raise Exception('FastAPI App not initialized')

            return getattr(self._app, attr)

    async def __call__(self, *args, **kwargs):
        self.http()
        await self._app.__call__(*args, **kwargs)

    def _launch_http(self):
        self._app = FastAPI(**self.base_settings)
        uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, access_log=True)

    def _launch_rpc(self):
        service = self.kwargs.get('rpc_service')
        if not service:
            raise Exception('rpc_service not provided')
        service.serve()

    def _start_all(self):
        process_http = Process(target=self._launch_http)
        process_http.start()
        process_rpc = Process(target=self._launch_rpc)
        process_rpc.start()
        process_rpc.join()
        process_http.join()

    def settings(self, **kwargs):
        self.base_settings.update(kwargs)

    def http(self):
        """load FastAPI to instance"""
        self._app = FastAPI(**self.base_settings)
        # routers
        for router in self.kwargs.get('routers', []):
            self._app.include_router(**router)
        # cors
        backend_cors_origins = self.kwargs.get('backend_cors_origins')
        if backend_cors_origins:
            self._app.add_middleware(
                CORSMiddleware,
                allow_origins=[str(origin) for origin in backend_cors_origins],
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )
            self._app.middleware('http')(process_middleware)

    def launch(self, http: bool = False, rpc: bool = False):
        start_all = not any([http, rpc])
        if start_all:
            return self._start_all()

        if http:
            self._launch_http()

        if start_all or rpc:
            self._launch_rpc()

    def start(self):
        typer.run(self.launch)
