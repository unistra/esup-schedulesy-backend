from __future__ import absolute_import, unicode_literals
import os

from celery import Celery
from celery.schedules import crontab
from kombu import Exchange, Queue

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'schedulesy.settings.{{ goal }}')

from django.conf import settings

celery_app = Celery(
    settings.CELERY_NAME,
    broker=settings.BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

celery_app.config_from_object('django.conf:settings')
celery_app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

exchange = Exchange('schedulesy', type='topic', durable=False, delivery_mode=1)

celery_app.conf.task_queues = (
    Queue('schedulesy', exchange, routing_key='schedulesy.test'),
)

celery_app.conf.task_default_queue = 'schedulesy'
celery_app.conf.task_default_exchange = 'schedulesy'
celery_app.conf.task_default_routing_key = 'schedulesy.test'

celery_app.conf.task_routes = [
    {
        'schedulesy.apps.refresh.tasks.test': {
            'queue': 'schedulesy',
            'routing_key': 'schedulesy.test',
        },
    },

]
