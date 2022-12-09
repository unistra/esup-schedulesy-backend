import logging
import pickle
import socket
import time
from datetime import datetime
from functools import wraps

import redis
from django.conf import settings
from redis.exceptions import LockError

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


r_redis_pool = None


def _redis_pool():
    global r_redis_pool
    if not r_redis_pool:
        logger.info(f"Initializing redis pool on {settings.CACHEOPS_REDIS_SERVER}")
        r_redis_pool = redis.ConnectionPool(
            host=settings.CACHEOPS_REDIS_SERVER,
            port=settings.CACHEOPS_REDIS_PORT,
            db=settings.CACHEOPS_REDIS_DB,
        )
    return r_redis_pool


def _redis():
    return redis.Redis(connection_pool=_redis_pool())


@doublewrap
def refresh_if_necessary(func, exclusivity=300):
    def wrapper(*args, **kwargs):
        # TODO: for unit test, find a better way to test this
        if not has_redis:
            func(*args, **kwargs)
            return

        r = _redis()

        key = key = func.__name__ + '-'.join(map(str, args))
        order_time = kwargs.get('order_time', time.time()) - exclusivity
        st = time.time()
        try:
            logger.info(f'Will lock {key}-lock')
            with r.lock(f'{key}-lock', timeout=300) as lock:
                if not r.exists(key) or float(r.get(key)) < order_time:
                    try:
                        func(*args, **kwargs)
                        r.set(key, time.time(), ex=3600)
                    except Exception as ex:
                        if lock.locked():
                            lock.release()
                        raise ex
                else:
                    logger.info(f'Prevented useless refresh for {key}')
        except LockError as exception:
            logger.error(f'[refresh_if_necessary] {func.__name__} {exception}')
            et = time.time()
            logger.warning(
                f'[refresh_if_necessary] Refresh of resource {key} was longer than lock : {et-st} seconds'
            )

    return wrapper


class MemoizeWithTimeout:
    """Memoize With Timeout"""

    def __init__(self, timeout=300):
        self.timeout = timeout
        if timeout < 1:
            self.timeout = 1

    def __call__(self, f):
        def func(*args, **kwargs):
            key = (
                f.__name__
                + '-'.join(map(str, args))
                + '-'.join(sorted(k + ':' + str(v) for k, v in kwargs.items()))
            )
            logger.debug(f'MemoizeWithTimeout {key}')
            r = _redis()
            if r.exists(key):
                v = pickle.loads(r.get(key))
            else:
                v = f(*args, **kwargs)
                r.set(key, pickle.dumps(v), ex=self.timeout)
            return v

        func.func_name = f.__name__
        return func
