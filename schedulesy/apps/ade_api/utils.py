import math
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


def hex_to_rgb(hex):
    return tuple(int(hex.lstrip('#')[i : i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(r, g, b):
    return f'#{r:02x}{g:02x}{b:02x}'


def get_pastel_colors():
    return list(map(hex_to_rgb, settings.PASTEL_COLORS))


def pastelize(to_pastelize, colors, format='rgb'):
    def rms(xs, ys):
        s = [(x - y) ** 2 for (x, y) in zip(xs, ys)]
        m = sum(s) / len(s)
        r = math.sqrt(m)
        return r

    def find_closest_color(r, g, b):
        colors.sort(key=lambda x: rms([x[0], x[1], x[2]], [r, g, b]))
        return colors[0]

    rgb = find_closest_color(*hex_to_rgb(to_pastelize))
    if format == 'hex':
        return rgb_to_hex(*find_closest_color(*hex_to_rgb(to_pastelize)))
    return rgb


def generate_color_from_name(name):
    """
    Generate a color from a name
    Uses uuid3 to generate a hex color from the name
    """
    namespace = uuid.NAMESPACE_DNS
    color = uuid.uuid3(namespace, name).hex
    return '#' + color[:6]
