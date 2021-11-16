import json
import logging
import time
import uuid
from json import JSONDecodeError

from celery import shared_task
from django.db.models import Q
from sentry_sdk import capture_exception
from skinos.custom_consumer import CustomConsumer

from schedulesy.apps.ade_api.models import Resource
from schedulesy.apps.ade_api.refresh import Refresh
from schedulesy.celery import sync_queue_name
from schedulesy.libs.decorators import async_log, refresh_if_necessary

logger = logging.getLogger(__name__)


@shared_task()
def refresh_all():
    refresh_agent = Refresh()
    refresh_agent.refresh_all()
    return refresh_agent.data


@shared_task(autoretry_for=(Exception,), default_retry_delay=60)
def refresh_resource(ext_id, *args, **kwargs):
    _refresh_resource(ext_id, *args, **kwargs)


@async_log
@refresh_if_necessary
def _refresh_resource(ext_id, *args, **kwargs):
    # TODO improve number of requests with batch size (file with uuid4)
    refresh_agent = Refresh()
    try:
        operation_id = (
            kwargs['operation_id'] if 'operation_id' in kwargs else str(uuid.uuid4())
        )
        refresh_agent.refresh_single_resource(ext_id, operation_id)
    except Exception as e:
        logger.error(e)
        raise e
    return None


@shared_task(autoretry_for=(Exception,), default_retry_delay=60)
def refresh_event(ext_id, activity_id, resources, batch_size, operation_id):
    # TODO improve number of requests with batch size (file with uuid4)
    refresh_agent = Refresh()
    refresh_agent.refresh_event(ext_id, activity_id, resources, operation_id)
    return None


@shared_task()
def bulldoze():
    resources = Resource.objects.filter(
        ~Q(ext_id__in=('classroom', 'instructor', 'trainee', 'category5'))
    )
    batch_size = len(resources)
    operation_id = str(uuid.uuid4())
    for resource in resources:
        refresh_resource.delay(
            resource.ext_id,
            batch_size=batch_size,
            operation_id=operation_id,
            order_time=time.time(),
        )


@CustomConsumer.consumer(
    sync_queue_name(), sync_queue_name(), sync_queue_name() + '.ade.*'
)
def refresh_resources(body, message):
    _refresh_resources(body, message)


@async_log
def _refresh_resources(body, message):
    """
    Awaited resources to refresh. All signals are from ADE sync
    :param body: JSON data / {"operation_id":"1e777a3f-0f9f-4bdb-8c07-61bb5286622e",
        "events":[{"resources":[1566,2565,2617,21184],"id":"163477"},
            {"resources":[12410,30964,362,13078],"id":"204538"}]}
    :param message: celery message
    :return: None
    """
    try:
        data = json.loads(body)
        operation_id = (
            str(uuid.uuid4()) if 'operation_id' not in data else data['operation_id']
        )

        resources_ids = _identify_resources(data)

        batch_size = len(resources_ids)
        logger.info(
            "{operation_id} / Will refresh {batch_size} resources".format(
                operation_id=operation_id, batch_size=batch_size
            )
        )

        for resource_id in resources_ids:
            refresh_resource.delay(
                resource_id,
                batch_size=batch_size,
                operation_id=operation_id,
                order_time=time.time(),
            )
    except JSONDecodeError as e:
        logger.error(f"Content : {body}\n{e}")
        capture_exception(e)


def _identify_resources(data):
    """
    Identifies resources linked to a refresh order.
    :param data: signal from ADE sync
    :return: array of ext_id (ADE ids)
    """
    old_resources = Resource.objects.raw(
        """
        SELECT DISTINCT(ade_api_resource.id)
        FROM ade_api_resource,
        jsonb_to_recordset(ade_api_resource.events->'events') as x(id int)
        WHERE x.id in %s
        """,
        params=[tuple(map(int, (value["id"] for value in data['events'])))],
    )
    old_resources_ids = {r.ext_id for r in old_resources}
    # Getting linked resources in new events
    resources = {
        str(item)
        for sublist in [
            value['resources'] for value in data['events'] if 'resources' in value
        ]
        for item in sublist
    }
    lineage = Resource.lineage(resources)
    # Finally adding original resources to list (for missing resources)
    resources_ids = set().union(old_resources_ids, lineage, resources)

    return resources_ids
