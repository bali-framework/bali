import hashlib
from functools import wraps
from urllib.parse import quote

from .cache import cache

MARKER = object()


def cache_memoize(timeout):
    def decorator(func):
        def _default_make_cache_key(*args, **kwargs):
            cache_key = "cache_memoize:" + ":".join(
                [quote("{}={}".format(k, v)) for k, v in kwargs.items()]
            )
            return hashlib.md5(cache_key.encode('utf-8')).hexdigest()

        _make_cache_key = _default_make_cache_key

        @wraps(func)
        def inner(*args, **kwargs):
            _refresh = bool(kwargs.pop('_refresh', False))
            cache_key = _make_cache_key(*args, **kwargs)
            if _refresh:
                result = MARKER
            else:
                result = cache.get(cache_key, MARKER)

            if result is MARKER:
                result = func(*args, **kwargs)
                cache.set(cache_key, result, timeout)
            return result

        # def invalidate(*args, **kwargs):
        #     kwargs.pop("_refresh", None)
        #     cache_key = _make_cache_key(*args, **kwargs)

        return inner

    return decorator
