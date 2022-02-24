"""Generic Routes

Generic routes include list/get/create/update/delete
Used by `resource.RouterGenerator`
"""

import inspect
import logging
import typing
from typing import Callable

from fastapi import Request

from ..paginate import paginate
from ..schemas import ListRequest


# noinspection PyUnresolvedReferences,PyProtectedMember
def list_(router_generator) -> Callable:
    """
    list action default using fastapi-pagination to process paginate
    """
    resource = router_generator.cls()

    # noinspection PyProtectedMember,PyShadowingNames,PyUnresolvedReferences
    def route(request: Request = None):
        resource._request = request
        router_generator.check_permissions(resource)
        params = request.query_params._dict

        # parse filters
        filters = {}
        for k, v in params.items():
            if k not in router_generator._ordered_filters:
                continue
            # noinspection PyBroadException
            try:
                # Convert param and retrieve param
                params_converter = router_generator._ordered_filters.get(k)
                if isinstance(params_converter, typing._GenericAlias):
                    params_converter = params_converter.__args__[0]
                filters[k] = params_converter(v)
            except Exception as ex:
                logging.warning(
                    'Query params `%s`(value: %s) type convert failed, '
                    'exception: %s', k, v, ex
                )
                continue

        schema_in = ListRequest(**params, filters=filters)

        result = getattr(resource, 'list')(schema_in)
        return paginate(result)

    # update route's signatures
    parameters = []
    for k, v in router_generator._ordered_filters.items():
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


def get_(self) -> Callable:
    resource = self.cls()
    action_func = getattr(resource, 'get')

    def route(id: int, request: Request = None):
        resource._request = request
        self.check_permissions(resource)
        return action_func(pk=id)

    async def async_route(id: int, request: Request = None):
        resource._request = request
        self.check_permissions(resource)
        return await action_func(pk=id)

    return async_route if inspect.iscoroutinefunction(action_func) else route


def create_(self) -> Callable:
    resource = self.cls()

    def route(schema_in: resource.schema, request: Request = None):
        resource._request = request
        self.check_permissions(resource)
        return getattr(resource, 'create')(schema_in)

    return route


def update_(self) -> Callable:
    resource = self.cls()

    def route(schema_in: resource.schema, id: int, request: Request = None):
        resource._request = request
        self.check_permissions(resource)
        return getattr(resource, 'update')(schema_in, pk=id)

    return route


def delete_(self) -> Callable:
    resource = self.cls()

    def route(id: int, request: Request = None):
        resource._request = request
        self.check_permissions(resource)
        return getattr(resource, 'delete')(pk=id)

    return route
