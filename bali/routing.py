import inspect

from fastapi import APIRouter as FastAPIRouter
from fastapi.routing import APIRoute as FastAPIRoute

from bali.core import db


class APIRoute(FastAPIRoute):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # inject sqlalchemy scope session remove to endpoint
        if not inspect.iscoroutinefunction(self.dependant.call):
            self.dependant.call = self._inject_scoped_session_clear(self.dependant.call)

    @staticmethod
    def _inject_scoped_session_clear(endpoint: callable):
        def injected_endpoint(*args, **kwargs):
            try:
                return endpoint(*args, **kwargs)
            finally:
                db.remove()

        return injected_endpoint


class APIRouter(FastAPIRouter):
    def add_api_route(self, *args, **kwargs):
        return super().add_api_route(*args, route_class_override=APIRoute, **kwargs)
