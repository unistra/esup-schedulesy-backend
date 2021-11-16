try:
    from .celery import celery_app
except ImportError:
    # Error raised by the "pip install -e ." in pydiploy due to the goal
    # template variable in celery.py
    pass


VERSION = (1, 1, 17)


def get_version():
    return '.'.join(map(str, VERSION[:3])) + ''.join(map(str, VERSION[3:]))
