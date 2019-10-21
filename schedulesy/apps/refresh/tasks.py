import json
import logging
import uuid
from json import JSONDecodeError

from celery import shared_task
from django.db.models import Q
from sentry_sdk import capture_exception
from skinos.custom_consumer import CustomConsumer

from schedulesy.apps.ade_api.models import Resource
from schedulesy.apps.ade_api.refresh import Refresh
from schedulesy.celery import sync_queue_name

logger = logging.getLogger(__name__)


@shared_task()
def refresh_all():
    refresh_agent = Refresh()
    refresh_agent.refresh_all()
    return refresh_agent.data


@shared_task()
def refresh_resource(ext_id, batch_size, operation_id):
    # TODO improve number of requests with batch size (file with uuid4)
    refresh_agent = Refresh()
    refresh_agent.refresh_resource(ext_id, operation_id)
    return None


@shared_task()
def refresh_event(ext_id, activity_id, resources, batch_size, operation_id):
    # TODO improve number of requests with batch size (file with uuid4)
    refresh_agent = Refresh()
    refresh_agent.refresh_event(ext_id, activity_id, resources, operation_id)
    return None


@shared_task()
def bulldoze():
    resources = Resource.objects \
        .filter(~Q(ext_id__in=('classroom', 'instructor', 'trainee',
                               'category5')))
    batch_size = len(resources)
    operation_id = str(uuid.uuid4())
    for resource in resources:
        refresh_resource.delay(resource.ext_id, batch_size, operation_id)


@CustomConsumer.consumer(sync_queue_name(), sync_queue_name() + ".ade", sync_queue_name() + '.ade.*')
def refresh_resources(body, message):
    """
    Awaited resources to refresh
    :param body: JSON data / {"operation_id":"1e777a3f-0f9f-4bdb-8c07-61bb5286622e", "resources":[26903]}
    :param message: celery message
    :return: None
    """
    try:
        print("{}".format(json.loads(body)))
    except JSONDecodeError as e:
        logger.error("Content : {}\n{}".format(body, e))
        capture_exception(e)
