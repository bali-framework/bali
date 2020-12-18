"""Bali Cache

Support redis backend 
"""
import pickle
from redis import StrictRedis

DEFAULT_TIMEOUT = 300


class Cache:
    def __init__(self):
        self.configured = False
        self.host = None
        self.port = None
        self.password = None
        self.prefix = None

        self._client = None

    def _connect(self):
        self._client = StrictRedis(self.host, port=self.port, password=self.password)

    def connect(self, host, port=6379, password=None, prefix=None):
        """
        Only support db 0
        """
        self.configured = True
        self.host = host
        self.port = port
        self.password = password
        self.prefix = prefix

        if self.prefix is None:
            raise Exception('Prefix should provided')

        self._connect()

    def __getattribute__(self, attr, *args, **kwargs):
        try:
            return super().__getattribute__(attr)
        except AttributeError:
            if not self._client:
                raise Exception('Cache client not initialized')

            return getattr(self._session, attr)

    def make_key(self, key):
        return f'{self.prefix}:cache:{key}'

    @staticmethod
    def encode(value):
        if isinstance(value, bool) or not isinstance(value, int):
            return pickle.dumps(value)
        return value

    @staticmethod
    def decode(value):
        try:
            value = int(value)
        except (ValueError, TypeError):
            value = pickle.loads(value)
        return value

    def set(self, key, value, timeout=DEFAULT_TIMEOUT):
        key = self.make_key(key)
        value = self.encode(value)
        return bool(self._client.set(key, value, ex=timeout))

    def get(self, key):
        key = self.make_key(key)
        value = self._client.get(key)
        if value is None:
            return value
        return self.decode(value)

    def _incr(self, key, delta=1):
        """Always check key exists
        """
        # if key expired after exists check, then we get
        # key with wrong value and ttl -1.
        # use lua script for atomicity
        lua = """
        local exists = redis.call('EXISTS', KEYS[1])
        if (exists == 1) then
            return redis.call('INCRBY', KEYS[1], ARGV[1])
        else return false end
        """
        value = self._client.eval(lua, 1, key, delta)
        if value is None:
            raise ValueError("Key '%s' not found" % key)

        return value

    def incr(self, key, delta=1):
        key = self.make_key(key)
        return self._incr(key, delta=delta)

    def decr(self, key, delta=1):
        key = self.make_key(key)
        return self._incr(key, delta=-delta)


cache = Cache()
