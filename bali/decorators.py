import functools

from fastapi.dependencies.utils import get_typed_signature
from fastapi_pagination import LimitOffsetParams, set_page
from fastapi_pagination.limit_offset import Page
from pydantic import BaseModel

from .exceptions import ReturnTypeError
from .paginate import paginate
from .utils import MessageToDict, ParseDict


def compatible_method(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):

        # Put args to inner function from request object
        if self._is_rpc:
            request_data = MessageToDict(
                self._request,
                including_default_value_fields=True,
                preserving_proto_field_name=True,
            )

            if func.__name__ == 'get':
                pk = self._request.id
                result = func(self, pk)
                if not isinstance(result, dict):
                    result = result.dict()
                response_data = {'data': result}

            elif func.__name__ == 'list':
                schema_in = get_schema_in(func)
                result = func(self, schema_in(**request_data))
                # Paginated the result queryset or iterable object
                if isinstance(result, BaseModel):
                    raise ReturnTypeError('Generic actions `list` should return a sequence')
                else:
                    set_page(Page)
                    params = LimitOffsetParams(
                        limit=request_data.get('limit') or 10,
                        offset=request_data.get('offset'),
                    )
                    response_data = paginate(result, params=params, is_rpc=True)

            elif func.__name__ in ['create', 'update']:
                schema_in = get_schema_in(func)
                data = request_data.get('data')
                result = func(self, schema_in(**data))
                if not isinstance(result, dict):
                    result = result.dict()
                response_data = {'data': result}

            elif func.__name__ == 'delete':
                pk = self._request.id
                result = func(self, pk)
                response_data = {'result': bool(result)}

            else:
                # custom action
                schema_in = get_schema_in(func)
                result = func(self, schema_in(**request_data))
                if not isinstance(result, dict):
                    result = result.dict()
                response_data = result

            # Convert response data to gRPC response
            return ParseDict(response_data, self._response_message(), ignore_unknown_fields=True)

        return func(self, *args, **kwargs)

    return wrapper


def action(methods=None, detail=None, **kwargs):
    """
    Mark a Resource method as a routable action.

    Set the `detail` boolean to determine if this action should apply to
    instance/detail requests or collection/list requests.

    :param methods:
    :param detail:
    :param kwargs:
        http_only: the action only support http
        rpc_only: the action only support rpc
    """
    methods = ['get'] if (methods is None) else methods
    methods = [method.lower() for method in methods]

    http_only = kwargs.get('http_only', False)
    rpc_only = kwargs.get('rpc_only', False)

    class Action:
        def __init__(self, func):
            self.func = func

        def __set_name__(self, owner, name):
            # replace ourself with the original method
            setattr(owner, name, compatible_method(self.func))

            # Append actions to Resource._actions
            # Only for http actions
            if rpc_only:
                return

            try:
                schema_in_annotation = get_schema_in(self.func)
            except ValueError:
                schema_in_annotation = None

            _actions = getattr(owner, '_actions')
            _actions[self.func.__name__] = {
                'detail': detail,
                'methods': methods,
                'schema_in_annotation': schema_in_annotation,
            }
            setattr(owner, '_actions', _actions)

    return Action


def get_schema_in(func):
    typed_signature = get_typed_signature(func)
    signature_params = typed_signature.parameters

    # 1st argument is self
    # 2st argument is schema_in
    index = 0
    for param_name, param in signature_params.items():
        index += 1
        if index == 2 or param_name == 'schema_in':
            schema_in = param.annotation
            if not schema_in:
                raise ValueError('Custom actions must provide `schema_in` argument with annotation')

            return schema_in
    else:
        raise ValueError('Custom actions arguments error')
