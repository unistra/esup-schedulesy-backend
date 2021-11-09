import json
import logging
from functools import wraps

import britney_utils
from britney.errors import SporeMethodCallError, SporeMethodStatusError
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from schedulesy.libs.decorators import MemoizeWithTimeout

from .exceptions import WSError

_clients = {}


def get_client(source, middlewares=None, reset=False, suffix='json', name='',
               **kwargs):
    global _clients

    source = source.upper()
    name = name or source
    # TODO: base_middlewares in settings
    base_middlewares = (
        ('ApiKey', {
            'key_name': 'Authorization',
            'key_value': 'Token {}'.format(
                getattr(settings, f'{source}WS_TOKEN'))
        }),
    )
    middlewares = base_middlewares + (middlewares or ())

    if source not in _clients:
        client = britney_utils.get_client(
            name,
            getattr(settings, f'{source}WS_DESCRIPTION'),
            base_url=getattr(settings, f'{source}WS_BASE_URL'),
            middlewares=middlewares,
            reset=reset,
            **kwargs
        )

        if suffix:
            client.add_default('format', suffix)
        _clients[source] = client

    return _clients[source]


def check_status(logger_name=__name__, object_type=''):
    def wrapper(func):
        obj_type = object_type\
            or func.__name__.replace('get_', '').rstrip('s')
        logger = logging.getLogger(logger_name)

        @wraps(func)
        def wrapped(*args, **kwargs):
            logger.debug('Getting %s', obj_type)
            try:
                response = func(*args, **kwargs)
            except SporeMethodStatusError as http_error:
                status = http_error.response.status_code
                if status == 401:
                    message = 'Webservice account can\'t authenticate'
                elif status == 403:
                    message = 'Webservice account needs some authorization'
                elif status >= 500:
                    message = 'Webservice seems to be down'
                else:
                    message = 'Error %s' % http_error.response.reason
                logger.critical(f'{status}: {message}')
                raise WSError(http_error.response, message, obj_type)
            except SporeMethodCallError as method_call_error:
                message = f'Bad function call: {method_call_error.cause}'
                logger.critical(message)
                logger.critical('Expected values: %s',
                                ', '.join(method_call_error.expected_values))
                raise WSError(None, message, obj_type)
            except Exception as exc:
                message = f'Unexpected error {exc.__class__.__name__} : {exc}'
                logger.critical(message)
                raise WSError(None, message, obj_type)
            else:
                logger.debug(response.request.url)
                return response
        return wrapped
    return wrapper


def format_json(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        response = func(*args, **kwargs).content
        return json.loads(response.decode('utf-8')) if response else None
    return wrapper


@MemoizeWithTimeout(timeout=360)
def get_geolocation(id, **kwargs):

    @format_json
    @check_status('infocentre')
    def get_building():
        return get_client('infocentre').get_building(
            id=id, fields='geolocation')

    # FIXME: useful ?
    # id = id or 0
    # Pfff whatever
    id = to_ade_id(id)
    if id:
        try:
            return get_building().get('geolocation', [])
        except Exception:
            pass
    return []


@MemoizeWithTimeout(timeout=600)
def get_geolocations(**kwargs):

    @format_json
    @check_status('infocentre')
    def get_buildings():
        return get_client('infocentre').list_buildings(fields='id,geolocation')

    return {b['id']: b['geolocation'] for b in get_buildings()}


def to_ade_id(id):
    # Lame way to check if the resource has an Abyla ID
    if id:
        if isinstance(id, int):
            return id
        if id.isdigit():
            return int(id)
    return None
