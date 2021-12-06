from django.conf import settings
from health_check.backends import BaseHealthCheckBackend
from health_check.exceptions import HealthCheckException


class ADECheckBackend(BaseHealthCheckBackend):
    critical_service = True

    def check_status(self):
        from schedulesy.apps.ade_legacy.models import Customization

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
        tasks = []
        try:
            from celery import Celery

            celery_app = Celery(
                settings.CELERY_NAME,
                broker=settings.BROKER_URL,
                backend=settings.CELERY_RESULT_BACKEND,
            )
            tasks = [
                worker
                for worker in celery_app.control.inspect().registered().values()
                if len(
                    list(filter(lambda x: x.startswith(settings.CELERY_NAME), worker))
                )
                > 0
            ]
        except Exception as e:
            raise HealthCheckException(e)
        if len(tasks) < 1:
            raise HealthCheckException("There is no active worker")

    def identifier(self):
        return self.__class__.__name__  # Display name on the endpoint.
