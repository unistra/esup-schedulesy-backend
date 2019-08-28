from django.core.exceptions import ObjectDoesNotExist
from rest_framework import permissions
from rest_framework.generics import (
    ListCreateAPIView, RetrieveUpdateDestroyAPIView)
from rest_framework.response import Response
from rest_framework.status import HTTP_404_NOT_FOUND

from schedulesy.apps.ade_legacy.serializers import CustomizationSerializer
from . import models


class CustomizationDetail(RetrieveUpdateDestroyAPIView):
    queryset = models.Customization.objects
    serializer_class = CustomizationSerializer
    lookup_field = 'username'

    def get(self, request, *args, **kwargs):
        try:
            obj = self.queryset.get(username=request.user.username)
        except ObjectDoesNotExist:
            return Response(status=HTTP_404_NOT_FOUND, data={'error': 'not found'})
        serializer = CustomizationSerializer(obj, context={'request': request})
        return Response(serializer.data)


class CustomizationList(ListCreateAPIView):
    queryset = models.Customization.objects
    serializer_class = CustomizationSerializer
    permission_classes = (permissions.IsAdminUser,)

    def list(self, request, *args, **kwargs):
        user = self.request.user
        if user.is_superuser:
            queryset = self.queryset
        else:
            queryset = self.queryset.filter(username=user.username)
        serializer = CustomizationSerializer(queryset, many=True)
        return Response(serializer.data)
