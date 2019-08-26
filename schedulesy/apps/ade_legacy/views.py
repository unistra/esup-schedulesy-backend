from rest_framework.generics import RetrieveUpdateDestroyAPIView, ListCreateAPIView

from . import models
from . import serializers


class CustomizationDetail(RetrieveUpdateDestroyAPIView):
    queryset = models.Customization.objects.all()
    serializer_class = serializers.WEdtpersoSerializer
    lookup_field = 'username'

    def perform_authentication(self, request):
        m = request.META
        super().perform_authentication(request)


class CustomizationList(ListCreateAPIView):
    queryset = models.Customization.objects.all()
    serializer_class = serializers.WEdtpersoSerializer
