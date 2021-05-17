"""Bali Resource

A Resource layer base class to handle FastAPI and gRPC requests and responses

Resource's method input is Pydantic schema

"""
import logging
import inspect
from collections import OrderedDict
from typing import Optional, Callable

import typing
from fastapi import Request, HTTPException, status
from fastapi_pagination import LimitOffsetPage, paginate
from google.protobuf import message
from pydantic import BaseModel

from .routing import APIRouter
from .schemas import ListRequest, ResultResponse

__all__ = ['Resource']


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


# noinspection PyShadowingBuiltins,PyUnresolvedReferences,PyProtectedMember,PyShadowingNames,DuplicatedCode
class RouterGenerator:
    """
    Generator router from Resource class
    """
    def __init__(self, cls):
        self.cls = cls
        self.router = APIRouter()
        self._ordered_filters = self._get_ordered_filters()

    def __call__(self):
        # noinspection PyProtectedMember
        for action, extra in self.cls._actions.items():
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

    def _list(self) -> Callable:
        """
        list action default using fastapi-pagination to process paginate
        """
        resource = self.cls()

        def route(request: Request = None):
            self.check_permissions(resource)
            params = request.query_params._dict

            # parse filters
            filters = {}
            for k, v in params.items():
                if k not in self._ordered_filters:
                    continue
                # noinspection PyBroadException
                try:
                    # Convert param and retrieve param
                    params_converter = self._ordered_filters.get(k)
                    if isinstance(params_converter, typing._GenericAlias):
                        params_converter = params_converter.__args__[0]
                    filters[k] = params_converter(v)
                except Exception as ex:
                    logging.warning(
                        'Query params `%s`(value: %s) type convert failed, exception: %s', k, v, ex
                    )
                    continue

            schema_in = ListRequest(**params, filters=filters)

            result = getattr(resource, 'list')(schema_in)
            if isinstance(result, BaseModel):
                return result
            else:
                return paginate(result)

        # update route's signatures
        parameters = []
        for k, v in self._ordered_filters.items():
            default = inspect.Parameter.empty
            if isinstance(v, typing._GenericAlias):
                default = None if type(None) in v.__args__ else default
            parameters.append(
                inspect.Parameter(
                    name=k,
                    kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    default=default,
                    annotation=v,
                )
            )
        sig = inspect.signature(route)
        parameters.extend(sig.parameters.values())
        route.__signature__ = sig.replace(parameters=parameters)

        return route

    def _get(self) -> Callable:
        resource = self.cls()

        def route(id: int):
            self.check_permissions(resource)
            return getattr(resource, 'get')(pk=id)

        return route

    def _create(self) -> Callable:
        resource = self.cls()

        def route(schema_in: resource.schema):
            self.check_permissions(resource)
            return getattr(resource, 'create')(schema_in)

        return route

    def _update(self) -> Callable:
        resource = self.cls()

        def route(schema_in: resource.schema, id: int):
            self.check_permissions(resource)
            return getattr(resource, 'update')(schema_in, pk=id)

        return route

    def _delete(self) -> Callable:
        resource = self.cls()

        def route(id: int):
            self.check_permissions(resource)
            return getattr(resource, 'delete')(pk=id)

        return route

    def get_endpoint(self, action, detail=False, schema=None):
        """Convert Resource instance method to FastAPI endpoint"""
        resource = self.cls()

        def endpoint():
            self.check_permissions(resource)
            return getattr(resource, action)()

        def endpoint_detail(pk: int):
            self.check_permissions(resource)
            return getattr(resource, action)(pk)

        def endpoint_schema(schema_in: BaseModel):
            self.check_permissions(resource)
            return getattr(resource, action)(schema_in)

        sig = inspect.signature(getattr(self.cls, action))

        route = endpoint
        if detail:
            route = endpoint_detail
        elif 'schema_in' in sig.parameters:
            route = endpoint_schema
            params = list(sig.parameters.values())[1:]
            route.__signature__ = sig.replace(parameters=params)

        return route

    def add_route(self, action, extra):
        if action == 'list':
            self.router.add_api_route(
                '',
                self._list(),
                methods=['GET'],
                response_model=LimitOffsetPage[self.cls.schema],
                summary=f'List {self.resource_name}'
            )
        elif action == 'create':
            self.router.add_api_route(
                '',
                self._create(),
                methods=['POST'],
                response_model=self.cls.schema and Optional[self.cls.schema],
                summary=f'Create {self.resource_name}'
            )
        elif action == 'get':
            self.router.add_api_route(
                '/{%s}' % self.primary_key,
                self._get(),
                methods=['GET'],
                response_model=self.cls.schema,
                summary=f'Get {self.resource_name}'
            )
        elif action == 'update':
            self.router.add_api_route(
                '/{%s}' % self.primary_key,
                self._update(),
                methods=['PATCH'],
                response_model=self.cls.schema,
                summary=f'Update {self.resource_name}'
            )
        elif action == 'delete':
            self.router.add_api_route(
                '/{%s}' % self.primary_key,
                self._delete(),
                methods=['DELETE'],
                response_model=ResultResponse,
                summary=f'Delete {self.resource_name}'
            )
        else:
            detail = extra.get('detail')
            methods = extra.get('methods')
            path = '/{%s}' % self.primary_key if detail else ''
            self.router.add_api_route(
                f"{path}/{action.replace('_', '-')}",
                self.get_endpoint(action, detail),
                methods=methods,
                summary=f"{action.replace('_', ' ')}"
            )
