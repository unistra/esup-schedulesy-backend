import uuid

import pytz
from django.conf import settings


def force_https(uri):
    if settings.STAGE != 'dev' and uri[:5] != 'https':
        uri = uri.replace('http://', 'https://')
    return uri


def generate_uuid():
    return str(uuid.uuid4())


def get_ade_timezone():
    return pytz.timezone(settings.ADE_DEFAULT_TIMEZONE)


def generate_color_from_name(name):
    """
    Generate a color from a name
    Uses uuid3 to generate a hex color from the name
    """
    namespace = uuid.NAMESPACE_DNS
    color = uuid.uuid3(namespace, name).hex
    return '#' + color[:6]
