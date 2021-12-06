from health_check.backends import BaseHealthCheckBackend
from health_check.exceptions import HealthCheckException

from schedulesy.apps.ade_legacy.models import Customization
from schedulesy.apps.refresh.tasks import health_check


class ADECheckBackend(BaseHealthCheckBackend):
    critical_service = True

    def check_status(self):
        try:
            c = Customization.objects.count()
        except Exception as e:
            raise HealthCheckException(e)
        if c < 1:
            raise HealthCheckException('Seems to have no Customization')

    def identifier(self):
        return self.__class__.__name__  # Display name on the endpoint.


class WorkerBackend(BaseHealthCheckBackend):
    critical_service = False

    def check_status(self):
        try:
            check = health_check.delay()
        except Exception as e:
            raise HealthCheckException(e)
        if check.get() != 'ok':
            raise HealthCheckException('Seems to have an issue with Celery worker')

    def identifier(self):
        return self.__class__.__name__  # Display name on the endpoint.
