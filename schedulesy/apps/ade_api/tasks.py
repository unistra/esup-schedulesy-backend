import json
import logging
import uuid
from datetime import datetime

from celery import shared_task
from django.conf import settings
from elasticsearch import Elasticsearch
from ua_parser import user_agent_parser

logger = logging.getLogger(__name__)

has_elasticsearch = 'schedulesy.middleware.StatsMiddleware' in settings.MIDDLEWARE


@shared_task(autoretry_for=(Exception,), default_retry_delay=60)
def stats(payload):
    if has_elasticsearch:
        if 'http_user_agent' in payload:
            try:
                payload.update({'user_agent': user_agent_parser.Parse(payload['http_user_agent'])})
            except Exception as e:
                logger.error(f'{e}')
        es = Elasticsearch([{'host': settings.ELASTIC_SEARCH_SERVER, 'port': settings.ELASTIC_SEARCH_PORT}])
        suffix = datetime.now().strftime('%Y%m')
        es.index(index=f'schedulesy-{suffix}', doc_type='doc', id=str(uuid.uuid4()), body=json.dumps(payload))
