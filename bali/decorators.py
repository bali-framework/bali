def action(methods=None, detail=None, url_path=None, **kwargs):
    """
    Mark a Resource method as a routable action.

    Set the `detail` boolean to determine if this action should apply to
    instance/detail requests or collection/list requests.
    """
    methods = ['get'] if (methods is None) else methods
    methods = [method.lower() for method in methods]

    assert detail is not None, ("@action() missing required argument: 'detail'")

    class Action:
        def __init__(self, func):
            self.func = func

        def __set_name__(self, owner, name):

            # Append actions to Resource._actions
            _actions = getattr(owner, '_actions')
            _actions[self.func.__name__] = {
                'detail': detail,
                'methods': methods,
            }
            setattr(owner, '_actions', _actions)

            # then replace ourself with the original method
            setattr(owner, name, self.func)

    return Action
