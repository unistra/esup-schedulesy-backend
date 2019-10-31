import uuid

from django.conf import settings
import pytz


def force_https(uri):
    if settings.STAGE != 'dev' and uri[:5] != 'https':
        uri = uri.replace('http://', 'https://')
    return uri


def generate_uuid():
    return str(uuid.uuid4())


def get_ade_timezone():
    return pytz.timezone(settings.ADE_DEFAULT_TIMEZONE)
