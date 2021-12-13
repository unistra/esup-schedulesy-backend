import logging
import socket
import time
from datetime import datetime
from functools import wraps

import redis
from django.conf import settings

from schedulesy import VERSION
from schedulesy.apps.ade_api.tasks import sync_log

logger = logging.getLogger(__name__)
has_redis = 'cacheops' in settings.INSTALLED_APPS


def async_log(func):
    def wrapper(*args, **kwargs):
        payload = {
            'task': func.__qualname__,
            'args': [str(x) for x in args if type(x) in (int, float, str)],
            'kwargs': kwargs,
            'server': socket.gethostname(),
            'environment': settings.STAGE,
            'version': '.'.join([str(x) for x in VERSION]),
            '@timestamp': datetime.now().isoformat(sep='T', timespec='milliseconds'),
        }
        start = time.perf_counter()
        try:
            func(*args, **kwargs)
        except Exception as e:
            payload.update({'error': str(e)})
            raise e
        finally:
            end = time.perf_counter()
            payload.update({'total': end - start})
            sync_log.delay(payload)

    return wrapper


def doublewrap(f):
    """
    a decorator decorator, allowing the decorator to be used as:
    @decorator(with, arguments, and=kwargs)
    or
    @decorator
    """

    @wraps(f)
    def new_dec(*args, **kwargs):
        if len(args) == 1 and len(kwargs) == 0 and callable(args[0]):
            # actual decorated function
            return f(args[0])
        else:
            # decorator arguments
            return lambda realf: f(realf, *args, **kwargs)

    return new_dec


@doublewrap
def refresh_if_necessary(func, exclusivity=3600):
    def wrapper(*args, **kwargs):
        # TODO: for unit test, find a better way to test this
        if not has_redis:
            func(*args, **kwargs)
            return

        r = redis.Redis(
            host=settings.CACHEOPS_REDIS_SERVER,
            port=settings.CACHEOPS_REDIS_PORT,
            db=settings.CACHEOPS_REDIS_DB,
        )

        def _key(name, *args):
            suffix = 'no_suffix'
            if len(args) >= 0:
                s = '-'.join(
                    map(str, filter(lambda x: isinstance(x, (str, int)), args))
                )
                if s != "":
                    suffix = s
            return f'{name}-{suffix}'

        key = _key(func.__name__, *args)
        order_time = kwargs.get('order_time', time.time()) - exclusivity
        with r.lock(f'{key}-lock', timeout=300) as _:
            if not r.exists(key) or float(r.get(key)) < order_time:
                func(*args, **kwargs)
                r.set(key, time.time(), ex=3600)
            else:
                logger.debug(f'Prevented useless {key}')

    return wrapper


class MemoizeWithTimeout:
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
