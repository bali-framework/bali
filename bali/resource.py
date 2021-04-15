"""Bali Resource

A Resource layer base class to handle FastAPI and gRPC requests and responses

Resource's method input is Pydantic schema

"""
import types

import decamelize

from typing import Optional, List, Callable

from .routing import APIRouter
from .schemas import ResultResponse

__all__ = ['Resource']

GENERIC_ACTIONS = [
    'get',
    'list',
    'create',
    'update',
    'delete',
]


class Resource:
    """Base Resource"""

    # Resource's name, should automatic recognition is not provided
    name = None

    schema = None

    _actions = GENERIC_ACTIONS

    @classmethod
    def as_router(cls):
        return RouterGenerator(cls)()


# noinspection PyShadowingBuiltins
class RouterGenerator:
    """
    Generator router from Resource class
    """
    def __init__(self, cls):
        self.cls = cls
        self.router = APIRouter()

    def __call__(self):
        # noinspection PyProtectedMember
        for action in self.cls._actions:
            if not hasattr(self.cls, action):
                continue
            self.add_route(action)
        return self.router

    @property
    def resource_name(self):
        return self.cls.__name__.replace('Resource', '')

    @property
    def primary_key(self):
        # return f'{decamelize.convert(self.resource_name)}_id'
        return 'id'

    def _list(self) -> Callable:
        resource = self.cls()

        def route(id: int):
            return getattr(resource, 'get')(pk=id)

        return route

    def _get(self) -> Callable:
        resource = self.cls()

        def route(id: int):
            return getattr(resource, 'get')(pk=id)

        return route

    def _create(self) -> Callable:
        resource = self.cls()

        def route(schema_in: resource.schema):
            return getattr(resource, 'create')(schema_in)

        return route

    def _update(self) -> Callable:
        resource = self.cls()

        def route(schema_in: resource.schema, id: int):
            return getattr(resource, 'update')(schema_in, pk=id)

        return route

    def _delete(self) -> Callable:
        resource = self.cls()

        def route(id: int):
            return getattr(resource, 'delete')(pk=id)

        return route

    def get_endpoint(self, action, detail=False, schema=None):
        """Convert Resource instance method to FastAPI endpoint"""
        resource = self.cls()

        def endpoint():
            return getattr(resource, action)()

        function_string = """
def endpoint_detail({args}):
    if {primary_key}.isdigit():
        {primary_key} = int({primary_key})
    return getattr(resource, action)(pk={primary_key})
""".format(
            args=f'schema_in: resource.schema, {self.primary_key}',
            primary_key=self.primary_key,
        )

        module_code = compile(function_string, '', 'exec')
        function_code = [c for c in module_code.co_consts if isinstance(c, types.CodeType)][0]
        base_globals = {}
        # noinspection PyTypeChecker
        base_globals.update(__builtins__, resource=resource, action=action)
        endpoint_detail = types.FunctionType(function_code, base_globals)

        return endpoint_detail if detail else endpoint

    def add_route(self, action):
        if action == 'list':
            self.router.add_api_route(
                '',
                self._list(),
                methods=['GET'],
                response_model=self.cls.schema and Optional[List[self.cls.schema]],
                summary=f'List {self.resource_name}'
            )
        if action == 'create':
            self.router.add_api_route(
                '',
                self._create(),
                methods=['POST'],
                response_model=self.cls.schema and Optional[self.cls.schema],
                summary=f'Create {self.resource_name}'
            )
        if action == 'get':
            self.router.add_api_route(
                '/{%s}' % self.primary_key,
                self._get(),
                methods=['GET'],
                response_model=self.cls.schema,
                summary=f'Get {self.resource_name}'
            )
        if action == 'update':
            self.router.add_api_route(
                '/{%s}' % self.primary_key,
                self._update(),
                methods=['PATCH'],
                response_model=self.cls.schema,
                summary=f'Update {self.resource_name}'
            )
        if action == 'delete':
            self.router.add_api_route(
                '/{%s}' % self.primary_key,
                self._delete(),
                methods=['DELETE'],
                response_model=ResultResponse,
                summary=f'Delete {self.resource_name}'
            )
