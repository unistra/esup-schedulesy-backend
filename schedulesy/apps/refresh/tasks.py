import json
import logging
import uuid
from json import JSONDecodeError

from celery import shared_task
from django.db.models import Q
from sentry_sdk import capture_exception
from skinos.custom_consumer import CustomConsumer

from schedulesy.apps.ade_api.models import Resource, LocalCustomization
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


@shared_task()
def generate_ics(r_id):
    lc = LocalCustomization.objects.get(pk=r_id)
    lc.generate_ics_calendar()


@CustomConsumer.consumer(sync_queue_name(), sync_queue_name() + ".ade", sync_queue_name() + '.ade.*')
def refresh_resources(body, message):
    """
    Awaited resources to refresh. All signals are from ADE sync
    :param body: JSON data / {"operation_id":"1e777a3f-0f9f-4bdb-8c07-61bb5286622e", "events":[154613, 16011, 69775]}
    :param message: celery message
    :return: None
    """
    try:
        data = json.loads(body)
        query = Q()
        queries = [Q(events__events__contains=[{'id': str(value)}]) for value in data['events']]
        if 'operation_id' not in data:
            operation_id = str(uuid.uuid4())
        else:
            operation_id = data['operation_id']
        for item in queries:
            query |= item
        resources = Resource.objects.filter(query)
        resources_ids = {v.ext_id: v for v in resources}
        # for ext_id in data['events']:
        #     resources = Resource.objects.filter(events__events__contains=[{'id': str(ext_id)}])
        #     resources_ids = {**resources_ids, **{v.ext_id: v for v in resources}}
        batch_size = len(resources_ids)
        for resource_id in resources_ids.keys():
            refresh_resource.delay(resource_id, batch_size, operation_id)
        logger.debug(
            "{operation_id} / Will refresh {batch_size} "
            "resources : {resources_list}".format(
                operation_id=operation_id,
                batch_size=batch_size,
                resources_list=[
                    x.fields['name'] for x
                    in
                    resources_ids.values()]))
        customizations = LocalCustomization.objects.filter(resources__ext_id__in=resources_ids.keys())
        logger.debug(
            "{operation_id} / Will refresh {size} customizations".format(
                operation_id=operation_id,
                size=len(customizations)))
        for customization in customizations:
            generate_ics.delay(customization.id)
    except JSONDecodeError as e:
        logger.error("Content : {}\n{}".format(body, e))
        capture_exception(e)
