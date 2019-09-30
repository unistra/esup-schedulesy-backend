from __future__ import absolute_import, unicode_literals
import os
import socket

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

suffix = socket.gethostname() if settings.STAGE == 'dev' else ''

celery_app.config_from_object('django.conf:settings')
celery_app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

message_name = 'schedulesy' + suffix

exchange = Exchange(message_name, type='topic', durable=False, delivery_mode=1)

celery_app.conf.task_queues = (
    Queue(message_name, exchange, routing_key=message_name + '.test'),
)

celery_app.conf.task_default_queue = message_name
celery_app.conf.task_default_exchange = message_name
celery_app.conf.task_default_routing_key = message_name + '.test'

celery_app.conf.task_routes = [
    {
        'schedulesy.apps.refresh.tasks.test': {
            'queue': message_name,
            'routing_key': message_name + '.test',
        },
    },

]
