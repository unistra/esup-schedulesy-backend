from . import models
from . import serializers
from rest_framework import generics, filters


class WEdtpersoDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.Edtperso.objects.all()
    serializer_class = serializers.WEdtpersoSerializer


class WEdtpersoList(generics.ListCreateAPIView):
    queryset = models.Edtperso.objects.all()
    serializer_class = serializers.WEdtpersoSerializer
