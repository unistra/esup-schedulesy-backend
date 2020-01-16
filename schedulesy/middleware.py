"""
Middlewares.
"""
import json
import logging
import socket
import time
import uuid
from datetime import datetime

from django.conf import settings
from django.http import FileResponse
from sentry_sdk import capture_exception

from schedulesy.apps.ade_api.tasks import stats

LOGGER = logging.getLogger(__name__)


class StatsMiddleware:
    """
    Sends analytics data on response and request to AMQP
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        """
        Creates analytics data
        :param request: Django request
        :type request: django.http.request.HttpRequest
        :return: Django response
        :rtype: django.http.response.HttpResponse
        """
        request.log = {'application': 'schedulesy',
                       '@timestamp': datetime.now().isoformat(sep='T', timespec='milliseconds'),
                       'ip': self.get_client_ip(request),
                       'path': request.path,
                       'method': request.method,
                       'server': socket.gethostname(),
                       'http_user_agent': request.META.get('HTTP_USER_AGENT'),
                       'environment': settings.STAGE,
                       'user': self.get_user(request)
                       }
        self.process_request(request)
        try:
            response = self.get_response(request)
            self.process_response(request, response)
            LOGGER.debug(f'response status code {response.status_code}')
            if response.status_code >= 300:
                try:
                    request.log.update({'message': json.loads(response.content)})
                except Exception:
                    pass
            self._send_log(request.log)
        except Exception as call_exception:
            capture_exception(call_exception)
            request.log.update({'status_code': 500})
            self._send_log(request.log)
            raise call_exception

        return response

    def _send_log(self, data):
        """
        Sends log to AMQP
        :param data: log data
        :type data: dict
        :return: None
        """
        try:
            LOGGER.debug(data)
            stats.delay(json.dumps(data))
        except Exception as e_log:
            LOGGER.error(e_log)

    def process_request(self, request):
        """
        Called on request
        :param request: Django request
        :type request: django.http.request.HttpRequest
        :return: None
        """
        request.start_time = time.time()

    def process_response(self, request, response):
        """
        Called after generation of the response
        :param request: Django request
        :type request: django.http.request.HttpRequest
        :param response: Django response
        :type response: django.http.response.HttpResponse
        :return: untouched response
        :rtype: django.http.response.HttpResponse
        """
        total = time.time() - request.start_time
        data = {'time': total,
                'status_code': response.status_code,
                'size': response.get('Content-Length') if isinstance(response, FileResponse)
                        else len(response.content),
                }
        request.log.update(data)
        return response

    def get_client_ip(self, request):
        """
        Gets client IP
        :param request: Django request
        :type request: django.http.request.HttpRequest
        :return: IP address
        :rtype: str
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        return x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')

    def get_user(self, request):
        """
        Generates an uuid3 for username (or anonymous)
        :param request: Django request
        :type request: django.http.request.HttpRequest
        :return: uuid
        :rtype: str
        """
        user = request.user.username if request.user.is_authenticated else 'anonymous'
        return str(uuid.uuid3(uuid.NAMESPACE_DNS, user))
