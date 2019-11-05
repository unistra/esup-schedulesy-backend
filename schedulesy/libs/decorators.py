import logging
import time

import redis
from django.conf import settings

logger = logging.getLogger(__name__)


def refresh_if_necessary(func):
    def wrapper(*args, **kwargs):
        r = redis.Redis(host=settings.CACHEOPS_REDIS_SERVER,
                        port=settings.CACHEOPS_REDIS_PORT,
                        db=settings.CACHEOPS_REDIS_DB)
        suffix = args[0] if isinstance(args[0], str) or isinstance(args[0], int) else args[1]
        key = f'{func.__name__}-{suffix}'
        order_time = kwargs['order_time'] if 'order_time' in kwargs else time.time()
        with r.lock(f'{key}-lock') as lock:
            if not r.exists(key) or float(r.get(key)) < order_time:
                func(*args, **kwargs)
                r.set(key, time.time())
            else:
                logger.debug(f'Prevented useless {key}')

    return wrapper


class MemoizeWithTimeout(object):
    """Memoize With Timeout"""
    _caches = {}
    _timeouts = {}

    def __init__(self, timeout=300):
        self.timeout = timeout

    def collect(self):
        """Clear cache of results which have timed out"""
        ct = time.time()
        for func in self._caches:
            cache = {}
            for key in self._caches[func]:
                if (ct - self._caches[func][key][1]) < self._timeouts[func]:
                    cache[key] = self._caches[func][key]
            self._caches[func] = cache

    def __call__(self, f):
        self._caches.setdefault(f, {})
        cache = {}
        self._timeouts[f] = self.timeout

        def func(*args, **kwargs):
            kw = sorted(kwargs.items())
            key = (args, tuple(kw))
            try:
                v = self._caches[f][key]
                if (time.time() - v[1]) > self.timeout:
                    raise KeyError
            except KeyError:
                result = f(*args, **kwargs), time.time()
                v = cache[key] = result
                self._caches[f] = cache
            return v[0]

        func.func_name = f.__name__
        return func
