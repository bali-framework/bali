import functools
from pydantic import BaseModel
from .resource import GENERIC_ACTIONS
from .utils import MessageToDict, ParseDict


def compatible_method(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        print('self', self)
        print('self._is_rpc', self._is_rpc)

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

            result = func(self, *args, **kwargs)
            return ParseDict(result, self._response_message())

        return func(self, *args, **kwargs)

    return wrapper


def action(methods=None, detail=None, url_path=None, **kwargs):
    """
    Mark a Resource method as a routable action.

    Set the `detail` boolean to determine if this action should apply to
    instance/detail requests or collection/list requests.
    """
    methods = ['get'] if (methods is None) else methods
    methods = [method.lower() for method in methods]

    class Action:
        def __init__(self, func):
            self.func = func

        def __set_name__(self, owner, name):
            # replace ourself with the original method
            setattr(owner, name, compatible_method(self.func))

            if self.func.__name__ in GENERIC_ACTIONS.keys():
                return

            # Append actions to Resource._actions
            _actions = getattr(owner, '_actions')
            _actions[self.func.__name__] = {
                'detail': detail,
                'methods': methods,
            }
            setattr(owner, '_actions', _actions)

    return Action
