from __future__ import absolute_import, unicode_literals

import os
import socket
from celery import Celery
from kombu import Exchange, Queue
from skinos.custom_consumer import CustomConsumer

from schedulesy.libs.decorators import MemoizeWithTimeout

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'schedulesy.settings.{{ goal }}')

from django.conf import settings

DEFAULT = '.default'
CALENDAR = '.ics'
SYNC = '.sync'


@MemoizeWithTimeout()
def queue_name():
    suffix = socket.gethostname() if settings.STAGE == 'dev' else ''
    return 'schedulesy' + suffix


def sync_queue_name():
    return queue_name() + SYNC


celery_app = Celery(
    settings.CELERY_NAME,
    broker=settings.BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

celery_app.config_from_object('django.conf:settings')
celery_app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

CustomConsumer.add_exchange(sync_queue_name(), sync_queue_name() + ".*.*")

message_name = queue_name()

exchange = Exchange(message_name, type='topic', durable=False, delivery_mode=1)

celery_app.conf.task_queues = (
    Queue(message_name, exchange, routing_key=message_name + DEFAULT),
    Queue(message_name + CALENDAR, exchange, routing_key=message_name + CALENDAR),
)

celery_app.conf.task_default_queue = message_name
celery_app.conf.task_default_exchange = message_name
celery_app.conf.task_default_routing_key = message_name + DEFAULT

celery_app.conf.task_routes = [
    {
        'schedulesy.apps.refresh.tasks.generate_ics': {
            'queue': message_name + CALENDAR,
            'routing_key': message_name + CALENDAR,
        },
    },
]

CustomConsumer.build(celery_app)
