import os
import socket

from celery import Celery
from kombu import Exchange, Queue
from skinos.custom_consumer import CustomConsumer

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'schedulesy.settings.{{ goal }}')

from django.conf import settings

from schedulesy.libs.decorators import MemoizeWithTimeout

DEFAULT = '.default'
CALENDAR = '.ics'
STATS = '.stats'
SYNC = '.sync'
SYNC_LOG = SYNC + '.log'


@MemoizeWithTimeout()
def queue_name():
    suffix = socket.gethostname() + 'local' if settings.STAGE == 'dev' else ''
    return 'schedulesy' + suffix


def sync_queue_name():
    return queue_name() + SYNC


celery_app = Celery(
    settings.CELERY_NAME,
    broker=settings.BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.config_from_object('django.conf:settings')
celery_app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

CustomConsumer.add_exchange(sync_queue_name(), sync_queue_name() + ".*.*")

message_name = queue_name()

exchange = Exchange(message_name, type='topic', durable=False, delivery_mode=1)

celery_app.conf.task_queues = (
    Queue(message_name, exchange, routing_key=message_name + DEFAULT),
    Queue(message_name + SYNC_LOG, exchange, routing_key=message_name + SYNC_LOG),
    Queue(message_name + STATS, exchange, routing_key=message_name + STATS),
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
        'schedulesy.apps.ade_api.tasks.stats': {
            'queue': message_name + STATS,
            'routing_key': message_name + STATS,
        },
        'schedulesy.apps.ade_api.tasks.sync_log': {
            'queue': message_name + SYNC_LOG,
            'routing_key': message_name + SYNC_LOG,
        },
    },
]

CustomConsumer.build(celery_app)
