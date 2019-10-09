from __future__ import absolute_import, unicode_literals

from .celery import celery_app

__all__ = ['celery_app']

VERSION = (1, 1, 0, 'rc', 1)


def get_version():
    return (
        '.'.join(map(str, VERSION[:3])) + ''.join(map(str, VERSION[3:])))
