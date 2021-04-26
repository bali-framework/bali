import functools
from pydantic import BaseModel
from .utils import MessageToDict, ParseDict


def compatible_method(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):

        # Put args to inner function from request object
        if self._is_rpc:
            if func.__name__ == 'get':
                pk = self._request.id
                result = func(self, pk)
                if isinstance(result, BaseModel):
                    result = result.dict()
                return ParseDict({'data': result}, self._response_message())

            elif func.__name__ == 'list':
                result = func(self, MessageToDict(self._request))
                # Paginated the result queryset or iterable object
                return result

            elif func.__name__ == 'create':
                result = func(self, MessageToDict(self._request))
                if isinstance(result, BaseModel):
                    result = result.dict()
                return ParseDict({'data': result}, self._response_message())

            elif func.__name__ == 'update':
                result = func(self, MessageToDict(self._request))
                if isinstance(result, BaseModel):
                    result = result.dict()
                return ParseDict({'data': result}, self._response_message())

            elif func.__name__ == 'delete':
                pk = self._request.id
                result = func(self, pk)
                return ParseDict({'result': bool(result)}, self._response_message())

            # custom action
            result = func(self, MessageToDict(self._request))
            if isinstance(result, BaseModel):
                result = result.dict()
            return ParseDict(result, self._response_message())

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

            _actions = getattr(owner, '_actions')
            _actions[self.func.__name__] = {
                'detail': detail,
                'methods': methods,
            }
            setattr(owner, '_actions', _actions)

    return Action
