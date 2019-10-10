import logging
import uuid

from celery import shared_task
from django.db.models import Q

from schedulesy.apps.ade_api.models import Resource
from schedulesy.apps.ade_api.refresh import Refresh

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
    resources = Resource.objects\
        .filter(~Q(ext_id__in=('classroom', 'instructor', 'trainee',
                               'category5')))
    batch_size = len(resources)
    operation_id = str(uuid.uuid4())
    for resource in resources:
        refresh_resource.delay(resource.ext_id, batch_size, operation_id)
