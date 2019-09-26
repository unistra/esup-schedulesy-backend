import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task() # utile pour les "reusable apps"
def test(a):
    print(a)
    return a
