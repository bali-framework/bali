import inspect
from typing import Callable

from fastapi import APIRouter as FastAPIRouter
from bali.core import db


class APIRouter(FastAPIRouter):
    @staticmethod
    def _inject_scoped_session_clear(endpoint: callable):
        def injected_endpoint():
            try:
                return endpoint()
            finally:
                db.remove()
        return injected_endpoint

    def add_api_route(self, path: str, endpoint: Callable, *args, **kwargs):
        # inject sqlalchemy scope session remove to endpoint
        if not inspect.iscoroutinefunction(endpoint):
            endpoint = self._inject_scoped_session_clear(endpoint)
        return super().add_api_route(path, endpoint, *args, **kwargs)
