from rest_framework.generics import RetrieveUpdateDestroyAPIView, ListCreateAPIView

from . import models
from . import serializers


class CustomizationDetail(RetrieveUpdateDestroyAPIView):
    queryset = models.Customization.objects.all()
    serializer_class = serializers.WEdtpersoSerializer


class CustomizationList(ListCreateAPIView):
    queryset = models.Customization.objects.all()
    serializer_class = serializers.WEdtpersoSerializer
