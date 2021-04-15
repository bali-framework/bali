import functools


def action(methods=None, detail=None, url_path=None, **kwargs):
    """
    Mark a Resource method as a routable action.

    Set the `detail` boolean to determine if this action should apply to
    instance/detail requests or collection/list requests.
    """
    methods = ['get'] if (methods is None) else methods
    methods = [method.lower() for method in methods]

    assert detail is not None, (
        "@action() missing required argument: 'detail'"
    )

    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            print('self', self)
            return func(*args, **kwargs)

        return wrapper
    return decorator


# def action(methods=None, detail=None, url_path=None, url_name=None, **kwargs):
#     """
#     Mark a ViewSet method as a routable action.
#
#     Set the `detail` boolean to determine if this action should apply to
#     instance/detail requests or collection/list requests.
#     """
#     methods = ['get'] if (methods is None) else methods
#     methods = [method.lower() for method in methods]
#
#     assert detail is not None, (
#         "@action() missing required argument: 'detail'"
#     )
#
#     # name and suffix are mutually exclusive
#     if 'name' in kwargs and 'suffix' in kwargs:
#         raise TypeError("`name` and `suffix` are mutually exclusive arguments.")
#
#     def decorator(func):
#         func.mapping = MethodMapper(func, methods)
#
#         func.detail = detail
#         func.url_path = url_path if url_path else func.__name__
#         func.url_name = url_name if url_name else func.__name__.replace('_', '-')
#         func.kwargs = kwargs
#
#         # Set descriptive arguments for viewsets
#         if 'name' not in kwargs and 'suffix' not in kwargs:
#             func.kwargs['name'] = pretty_name(func.__name__)
#         func.kwargs['description'] = func.__doc__ or None
#
#         return func
#     return decorator
