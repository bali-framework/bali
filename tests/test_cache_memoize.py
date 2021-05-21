import hashlib
import os
import pickle
from urllib.parse import quote

from redis import StrictRedis

from bali.core import cache, cache_memoize

HOST = '127.0.0.1'
PREFIX = 'test_service'


def noop(*args):
    return args


args_rewrite = noop


def _default_make_cache_key(*args, prefix_=None, **kwargs):
    cache_key = "cache_memoize:" + ":" + prefix_ + ":".join(
        [quote(str(x)) for x in args_rewrite(args)] +
        [quote("{}={}".format(k, v)) for k, v in kwargs.items()]
    )
    return hashlib.md5(cache_key.encode('utf-8')).hexdigest()


@cache_memoize(30)
def foo():
    return '0'


@cache_memoize(30)
def foo_with_args(a):
    return f'0{a}'


class A:
    @cache_memoize(10)
    def foo(self):
        return 'A'

    @cache_memoize(10)
    def foo_with_args(self, a):
        return f'A{a}'

    @staticmethod
    @cache_memoize(10)
    def foo_with_args_s(a):
        return f'A{a}s'


class B:
    @cache_memoize(10)
    def foo(self):
        return 'B'

    @cache_memoize(10)
    def foo_with_args(self, a):
        return f'B{a}'

    @staticmethod
    @cache_memoize(10)
    def foo_with_args_s(a):
        return f'B{a}s'


class TestCacheMemoize:
    # noinspection PyMethodMayBeStatic
    def setup_class(self):
        self.redis = StrictRedis(HOST, password=os.getenv('CACHE_PASSWORD'))
        cache.connect(HOST, password=os.getenv('CACHE_PASSWORD'), prefix=PREFIX)

    def teardown_class(self):
        pass

    def test_cache_into_redis(self):
        expect_value = foo()
        prefix_ = ".".join((foo.__module__ or "", foo.__qualname__))
        key = _default_make_cache_key(prefix_=prefix_)
        redis_key = f'{PREFIX}:cache:{key}'
        result = pickle.loads(self.redis.get(redis_key))
        assert result == expect_value, 'Cache into redis verify failed'

    def test_cache_same_function_name_not_conflict(self):
        """Same function name in different module should not conflict"""
        a = A()
        b = B()
        value_a = a.foo()
        value_b = b.foo()
        assert value_a == 'A'
        assert value_b == 'B'

        # value a in redis
        prefix_ = ".".join((a.foo.__module__ or "", a.foo.__qualname__))
        key = _default_make_cache_key(a, prefix_=prefix_)
        redis_key = f'{PREFIX}:cache:{key}'
        result_a = pickle.loads(self.redis.get(redis_key))

        # value b in redis
        prefix_ = ".".join((b.foo.__module__ or "", b.foo.__qualname__))
        key = _default_make_cache_key(b, prefix_=prefix_)
        redis_key = f'{PREFIX}:cache:{key}'
        result_b = pickle.loads(self.redis.get(redis_key))

        assert result_a == value_a
        assert result_b == value_b

    def test_cache_same_function_args_not_conflict(self):
        """Same function name with args in different module should not conflict"""
        a = A()
        b = B()
        value_a = a.foo_with_args('9')
        value_b = b.foo_with_args('9')
        assert value_a == 'A9'
        assert value_b == 'B9'

        # value a in redis
        prefix_ = ".".join((a.foo_with_args.__module__ or "", a.foo_with_args.__qualname__))
        key = _default_make_cache_key(a, '9', prefix_=prefix_)
        redis_key = f'{PREFIX}:cache:{key}'
        result_a = pickle.loads(self.redis.get(redis_key))

        # value b in redis
        prefix_ = ".".join((b.foo_with_args.__module__ or "", b.foo_with_args.__qualname__))
        key = _default_make_cache_key(b, '9', prefix_=prefix_)
        redis_key = f'{PREFIX}:cache:{key}'
        result_b = pickle.loads(self.redis.get(redis_key))

        assert result_a == value_a
        assert result_b == value_b

    def test_cache_same_static_function_name_not_conflict(self):
        """Same static function name in different module should not conflict"""
        a = A()
        b = B()
        value_a = a.foo_with_args_s('1')
        value_b = b.foo_with_args_s('1')
        assert value_a == 'A1s'
        assert value_b == 'B1s'

        # value a in redis
        prefix_ = ".".join((a.foo_with_args_s.__module__ or "", a.foo_with_args_s.__qualname__))
        key = _default_make_cache_key('1', prefix_=prefix_)
        redis_key = f'{PREFIX}:cache:{key}'
        result_a = pickle.loads(self.redis.get(redis_key))

        # value b in redis
        prefix_ = ".".join((b.foo_with_args_s.__module__ or "", b.foo_with_args_s.__qualname__))
        key = _default_make_cache_key('1', prefix_=prefix_)
        redis_key = f'{PREFIX}:cache:{key}'
        result_b = pickle.loads(self.redis.get(redis_key))

        assert result_a == value_a
        assert result_b == value_b
