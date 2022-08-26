import json
import logging
import uuid
from datetime import datetime

from celery import shared_task
from django.conf import settings
from ua_parser import user_agent_parser

logger = logging.getLogger(__name__)

has_elasticsearch = 'schedulesy.middleware.StatsMiddleware' in settings.MIDDLEWARE


@shared_task(autoretry_for=(Exception,), default_retry_delay=60)
def sync_log(payload):
    log(payload, 'ade-sync')


@shared_task(autoretry_for=(Exception,), default_retry_delay=60)
def stats(payload):
    log(payload, 'schedulesy')


def log(payload, prefix):
    if 'http_user_agent' in payload:
        if not payload['http_user_agent']:
            payload.update({'http_user_agent': ''})
        try:
            payload.update(
                {'user_agent': user_agent_parser.Parse(payload['http_user_agent'])}
            )
        except Exception as e:
            logger.error(f'{e}\n{payload}')
    # suffix = datetime.now().strftime('%Y%m')
    payload.update({'application': prefix})
    logger.info(json.dumps(payload))
