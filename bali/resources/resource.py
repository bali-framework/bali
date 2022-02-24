"""Bali Resource

A Resource layer base class to handle FastAPI and gRPC requests and responses

Resource's method input is Pydantic schema

"""
import inspect
import logging
import typing
from collections import OrderedDict
from typing import Optional, Callable

from fastapi import Request, HTTPException, status
from fastapi_pagination import LimitOffsetPage
from google.protobuf import message
from pydantic import BaseModel

from ..paginate import paginate
from ..routing import APIRouter
from ..schemas import ListRequest, ResultResponse
from .generic_routes import *

__all__ = ['Resource', 'GENERIC_ACTIONS']

GENERIC_ACTIONS = [
    'list',
    'get',
    'create',
    'update',
    'delete',
]


class Resource:
    """Base Resource

    Generic Actions is get, list, create, update, delete
    """

    # Resource's name, should automatic recognition is not provided
    name = None

    schema = None
    filters = []
    permission_classes = []

    _actions = OrderedDict()

    def __init__(self, request=None, context=None, response_message=None):
        self._request = request
        self._context = context
        self._response_message = response_message

        self._is_rpc = isinstance(self._request, message.Message)
        self._is_http = not self._is_rpc

        self.auth = BaseModel()

    @classmethod
    def as_router(cls):
        return RouterGenerator(cls)()


# noinspection PyShadowingBuiltins,PyUnresolvedReferences,PyProtectedMember
# noinspection PyShadowingNames,DuplicatedCode
class RouterGenerator:
    """
    Generator router from Resource class
    """
    def __init__(self, cls):
        self.cls = cls
        self.router = APIRouter()
        self._ordered_filters = self._get_ordered_filters()

    def __call__(self):

        # To fixed generic get action `/item/{id}` conflict with custom action `/item/hello`,
        # must make sure get action `/item/{id}` is below custom action
        actions = sorted(
            self.cls._actions.keys(), key=lambda x: x in GENERIC_ACTIONS
        )

        # noinspection PyProtectedMember
        for action in actions:
            extra = self.cls._actions.get(action)
            if not hasattr(self.cls, action):
                continue
            self.add_route(action, extra)
        return self.router

    @property
    def resource_name(self):
        return self.cls.__name__.replace('Resource', '')

    @property
    def primary_key(self):
        return 'id'

    def check_permissions(self, resource):
        for permission_class in self.cls.permission_classes:
            permission = permission_class(resource)
            if not permission.check():
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail='Permission Denied',
                )

    def _get_ordered_filters(self):
        filters = OrderedDict()
        for item in self.cls.filters:
            k = item.keys().__iter__().__next__()
            v = item.values().__iter__().__next__()
            filters[k] = v
        return filters

    def get_endpoint(
        self, action, detail=False, methods=list, schema_in_annotation=None
    ):
        """Convert Resource instance method to FastAPI endpoint"""
        resource = self.cls()
        action_func = getattr(resource, action)

        def endpoint(request: Request = None):
            resource._request = request
            self.check_permissions(resource)
            return action_func()

        async def async_endpoint(request: Request = None):
            resource._request = request
            self.check_permissions(resource)
            return await action_func()

        def endpoint_detail(pk: int, request: Request = None):
            resource._request = request
            self.check_permissions(resource)
            return action_func(pk)

        async def async_endpoint_detail(pk: int, request: Request = None):
            resource._request = request
            self.check_permissions(resource)
            return await action_func(pk)

        def endpoint_schema(
            schema_in: BaseModel = None, request: Request = None, **kwargs
        ):
            resource._request = request
            self.check_permissions(resource)
            if 'get' in methods and schema_in_annotation:
                schema_in = schema_in_annotation(**kwargs)
            return action_func(schema_in)

        async def async_endpoint_schema(
            schema_in: BaseModel = None, request: Request = None, **kwargs
        ):
            resource._request = request
            self.check_permissions(resource)
            if 'get' in methods and schema_in_annotation:
                schema_in = schema_in_annotation(**kwargs)
            return await action_func(schema_in)

        sig = inspect.signature(getattr(self.cls, action))

        route = pick_route(action_func, async_endpoint, endpoint)
        if detail:
            route = pick_route(
                action_func, async_endpoint_detail, endpoint_detail
            )
        elif 'schema_in' in sig.parameters:
            route = pick_route(
                action_func, async_endpoint_schema, endpoint_schema
            )
            params = list(sig.parameters.values())[1:]
            if 'get' in methods and schema_in_annotation:
                # Destructor the `schema_in` to Query
                for field, annotation in schema_in_annotation.__fields__.items(
                ):
                    params = params[1:]
                    params.append(
                        inspect.Parameter(
                            name=field,
                            kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
                            default=annotation.default,
                            annotation=annotation.type_,
                        )
                    )
                route.__signature__ = sig.replace(parameters=params)
            else:
                params = list(sig.parameters.values())[1:]

            params.append(
                inspect.Parameter(
                    name='request',
                    kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    default=None,
                    annotation=Request,
                )
            )
            route.__signature__ = sig.replace(parameters=params)

        return route

    def add_route(self, action, extra):
        if action == 'list':
            self.router.add_api_route(
                '',
                list_(self),
                methods=['GET'],
                response_model=LimitOffsetPage[self.cls.schema],
                summary=f'List {self.resource_name}'
            )
        elif action == 'create':
            self.router.add_api_route(
                '',
                create_(self),
                methods=['POST'],
                response_model=self.cls.schema and Optional[self.cls.schema],
                summary=f'Create {self.resource_name}'
            )
        elif action == 'get':
            self.router.add_api_route(
                '/{%s}' % self.primary_key,
                get_(self),
                methods=['GET'],
                response_model=self.cls.schema,
                summary=f'Get {self.resource_name}'
            )
        elif action == 'update':
            self.router.add_api_route(
                '/{%s}' % self.primary_key,
                update_(self),
                methods=['PATCH'],
                response_model=self.cls.schema,
                summary=f'Update {self.resource_name}'
            )
        elif action == 'delete':
            self.router.add_api_route(
                '/{%s}' % self.primary_key,
                delete_(self),
                methods=['DELETE'],
                response_model=ResultResponse,
                summary=f'Delete {self.resource_name}'
            )
        else:
            detail = extra.get('detail')
            methods = extra.get('methods')
            schema_in_annotation = extra.get('schema_in_annotation')
            path = '/{%s}' % self.primary_key if detail else ''
            self.router.add_api_route(
                f"{path}/{action.replace('_', '-')}",
                self.get_endpoint(
                    action,
                    detail,
                    methods=methods,
                    schema_in_annotation=schema_in_annotation,
                ),
                methods=methods,
                summary=f"{action.replace('_', ' ')}"
            )
