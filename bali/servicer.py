"""
gRPC servicer
"""
import logging
from concurrent import futures

import grpc

logger = logging.getLogger('bali')


class ServicerNotFound(Exception):
    pass


class ServicerMethodNotFound(Exception):
    pass


def get_servicer(app):
    base_servicer = None
    servicer = f'{app.title.capitalize()}ServiceServicer'
    if hasattr(app._pb2_grpc, servicer):
        base_servicer = getattr(app._pb2_grpc, servicer)

    servicer = f'{app.title.capitalize()}Servicer'
    if hasattr(app._pb2_grpc, servicer):
        base_servicer = getattr(app._pb2_grpc, servicer)

    if base_servicer:

        class Service(base_servicer):
            pass

        return Service

    raise ServicerNotFound()


# noinspection PyProtectedMember
def make_grpc_serve(app):
    from .interceptors import ProcessInterceptor

    servicer_method = f'add_{app.title.capitalize()}ServiceServicer_to_server'
    if not hasattr(app._pb2_grpc, servicer_method):
        servicer_method = f'add_{app.title.capitalize()}Servicer_to_server'
        if not hasattr(app._pb2_grpc, servicer_method):
            raise ServicerMethodNotFound()

    # noinspection PyProtectedMember
    def serve():
        port = 9080
        server = grpc.server(
            futures.ThreadPoolExecutor(max_workers=10),
            interceptors=[ProcessInterceptor()],
        )

        servicer = getattr(app._pb2_grpc, servicer_method)
        servicer(app._rpc_servicer(), server)
        server.add_insecure_port(f'[::]:{port}')
        server.start()
        logger.info("Service started on port: %s (env: %s)", port, 'default')
        server.wait_for_termination()

    return serve
