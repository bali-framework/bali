"""Generic Routes

Generic routes include list/get/create/update/delete
Used by `resource.RouterGenerator`

# TODO: Optimized boilerplate code

"""

import inspect
import logging
import typing
from typing import Callable

from fastapi import Request

from ..paginate import paginate
from ..schemas import ListRequest


# --- Utilities functions for route handler ---
def pick_route(func, async_route, route):
    """Pick coroutine or generic function for route"""
    return async_route if inspect.iscoroutinefunction(func) else route


# noinspection PyUnresolvedReferences,PyProtectedMember
def list_(router_generator) -> Callable:
    """
    list action default using fastapi-pagination to process paginate
    """
    resource = router_generator.cls()
    action_func = getattr(resource, 'list')

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

        result = action_func(schema_in)
        return paginate(result)

    # noinspection PyProtectedMember,PyShadowingNames,PyUnresolvedReferences
    async def async_route(request: Request = None):
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

        result = await action_func(schema_in)
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

    return pick_route(action_func, async_route, route)


def get_(router_generator) -> Callable:
    resource = router_generator.cls()
    action_func = getattr(resource, 'get')

    def route(id: int, request: Request = None):
        resource._request = request
        router_generator.check_permissions(resource)
        return action_func(pk=id)

    async def async_route(id: int, request: Request = None):
        resource._request = request
        router_generator.check_permissions(resource)
        return await action_func(pk=id)

    return pick_route(action_func, async_route, route)


def create_(router_generator) -> Callable:
    resource = router_generator.cls()
    action_func = getattr(resource, 'create')

    def route(schema_in: resource.schema, request: Request = None):
        resource._request = request
        router_generator.check_permissions(resource)
        return action_func(schema_in)

    async def async_route(schema_in: resource.schema, request: Request = None):
        resource._request = request
        router_generator.check_permissions(resource)
        return await action_func(schema_in)

    return pick_route(action_func, async_route, route)


def update_(router_generator) -> Callable:
    resource = router_generator.cls()
    action_func = getattr(resource, 'update')

    def route(schema_in: resource.schema, id: int, request: Request = None):
        resource._request = request
        router_generator.check_permissions(resource)
        return action_func(schema_in, pk=id)

    async def async_route(
        schema_in: resource.schema, id: int, request: Request = None
    ):
        resource._request = request
        router_generator.check_permissions(resource)
        return await action_func(schema_in, pk=id)

    return pick_route(action_func, async_route, route)


def delete_(router_generator) -> Callable:
    resource = router_generator.cls()
    action_func = getattr(resource, 'delete')

    def route(id: int, request: Request = None):
        resource._request = request
        router_generator.check_permissions(resource)
        return action_func(pk=id)

    async def async_route(id: int, request: Request = None):
        resource._request = request
        router_generator.check_permissions(resource)
        return await action_func(pk=id)

    return pick_route(action_func, async_route, route)
