import json
import logging
import socket
import time
from datetime import datetime

from django.conf import settings
from django.http import FileResponse

from schedulesy.apps.ade_api.tasks import stats

logger = logging.getLogger(__name__)

class StatsMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        self.process_request(request)
        response = self.get_response(request)
        self.process_response(request, response)
        return response

    def process_request(self, request):
        request.start_time = time.time()

    def process_response(self, request, response):
        total = time.time() - request.start_time
        size = response.get('Content-Length') if isinstance(response, FileResponse) else len(response.content)
        data = {'application': 'schedulesy',
                '@timestamp': datetime.now().isoformat(sep='T', timespec='auto'),
                'ip': request.META.get('REMOTE_ADDR'),
                'path': request.path,
                'method': request.method,
                'server': socket.gethostname(),
                'http_user_agent': request.META.get('HTTP_USER_AGENT'),
                'time': total,
                'status_code': response.status_code,
                'size': size,
                'environment': settings.STAGE,
                }
        # Add the header.
        try:
            stats.delay(json.dumps(data))
        except Exception as e:
            logger.error(e)
        return response
