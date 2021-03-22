import os
import pickle

import pytest

from bali.core import cache
from redis import StrictRedis

HOST = '127.0.0.1'
PREFIX = 'test_service'


class TestCache:
    # noinspection PyMethodMayBeStatic
    def setup_class(self):
        cache.connect(HOST, password=os.getenv('CACHE_PASSWORD'), prefix=PREFIX)

    def teardown_class(self):
        pass

    def test_cache_int(self):
        key = 'test_int'
        value = 1
        result = cache.set('test_int', value)
        assert result is True, 'Cache int value failed'

        redis = StrictRedis(HOST, password=os.getenv('CACHE_PASSWORD'))
        redis_key = f'{PREFIX}:cache:{key}'
        assert int(redis.get(redis_key).decode('utf-8')) == value, 'Cache int value verify failed'

        result = cache.get(key)
        assert result is value, 'Cache int value get failed'

    def test_cache_str(self):
        key = 'test_str'
        value = 'hello, bali'
        result = cache.set(key, value)
        assert result is True, 'Cache str value failed'

        redis = StrictRedis(HOST, password=os.getenv('CACHE_PASSWORD'))
        redis_key = f'{PREFIX}:cache:{key}'
        redis_result = pickle.loads(redis.get(redis_key))
        assert redis_result == value, 'Cache str value verify failed'

        result = cache.get(key)
        assert result == value, 'Cache str value get failed'

    def test_cache_list(self):
        key = 'test_list'
        value = [1, 2, 3, 'a', (1, 'zzz')]
        result = cache.set(key, value)
        assert result is True, 'Cache list value failed'

        redis = StrictRedis(HOST, password=os.getenv('CACHE_PASSWORD'))
        redis_key = f'{PREFIX}:cache:{key}'
        redis_result = pickle.loads(redis.get(redis_key))
        assert redis_result == value, 'Cache list value verify failed'

        result = cache.get(key)
        assert result == value, 'Cache list value get failed'

    def test_cache_dict(self):
        key = 'test_dict'
        value = {'test': 1, 'test2': 'test', 'test3': {'aa': 1}}
        result = cache.set(key, value)
        assert result is True, 'Cache dict value failed'

        redis = StrictRedis(HOST, password=os.getenv('CACHE_PASSWORD'))
        redis_key = f'{PREFIX}:cache:{key}'
        redis_result = pickle.loads(redis.get(redis_key))
        assert redis_result == value, 'Cache dict value verify failed'

        result = cache.get(key)
        assert result == value, 'Cache dict value get failed'

    def test_not_exists(self):
        result = cache.get('no-exist-key')
        assert result is None, 'Should return none when cache not exists'

    def test_incr_raise_ex(self):
        """
        incr a non exist key will raise ValueError exception
        """
        with pytest.raises(ValueError):
            cache.incr('no-exist-key')

    def test_incr(self):
        key = 'test_incr'
        cache.set(key, 0)
        next_value = cache.incr(key)
        assert next_value == 1
        next_value = cache.incr(key)
        assert next_value == 2
        next_value = cache.incr(key, 2)
        assert next_value == 4

    def test_decr(self):
        key = 'test_decr'
        cache.set(key, 0)
        next_value = cache.decr(key)
        assert next_value == -1
        next_value = cache.decr(key)
        assert next_value == -2
        next_value = cache.decr(key, 2)
        assert next_value == -4
