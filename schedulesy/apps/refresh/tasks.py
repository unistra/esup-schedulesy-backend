import logging

from celery import shared_task

from schedulesy.apps.ade_api.models import Resource
from schedulesy.apps.ade_api.refresh import Refresh

logger = logging.getLogger(__name__)


@shared_task()
def refresh_all():
    refresh_agent = Refresh()
    refresh_agent.refresh_all()
    return refresh_agent.data


@shared_task()
def refresh_resource(ext_id, batch_size):
    refresh_agent = Refresh()
    refresh_agent.refresh_resource(ext_id)
    return None

@shared_task()
def bulldoze():
    resources = [x for x in Resource.objects.all() if x.ext_id not in ['classroom', 'instructor', 'trainee', 'category5']]
    batch_size = len(resources)
    for resource in resources:
        refresh_resource.delay(resource.ext_id, batch_size)
