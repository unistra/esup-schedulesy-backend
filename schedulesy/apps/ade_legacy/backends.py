from health_check.backends import BaseHealthCheckBackend
from health_check.exceptions import HealthCheckException

from schedulesy.apps.ade_legacy.models import Customization


class ADECheckBackend(BaseHealthCheckBackend):
    #: The status endpoints will respond with a 200 status code
    #: even if the check errors.
    critical_service = False

    def check_status(self):
        try:
            c = Customization.objects.count()
        except Exception as e:
            raise HealthCheckException(e)
        if c < 1:
            raise HealthCheckException('Seems to have no Customization')

    def identifier(self):
        return self.__class__.__name__  # Display name on the endpoint.
