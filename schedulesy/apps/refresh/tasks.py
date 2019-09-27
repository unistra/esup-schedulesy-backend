import logging

from celery import shared_task

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
