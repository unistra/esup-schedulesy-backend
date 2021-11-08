import json
import logging

from rest_framework.generics import (
    ListCreateAPIView, RetrieveUpdateDestroyAPIView)
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.status import HTTP_409_CONFLICT

from schedulesy.apps.ade_legacy.serializers import CustomizationSerializer
from schedulesy.libs.permissions import IsOwnerPermission
from . import models

logger = logging.getLogger(__name__)


class CustomizationDetail(RetrieveUpdateDestroyAPIView):

    permission_classes = (
        api_settings.DEFAULT_PERMISSION_CLASSES + [IsOwnerPermission])
    queryset = models.Customization.objects.all()
    serializer_class = CustomizationSerializer
    lookup_field = 'username'


class CustomizationList(ListCreateAPIView):
    queryset = models.Customization.objects.all()
    serializer_class = CustomizationSerializer
    permission_classes = (
        api_settings.DEFAULT_PERMISSION_CLASSES + [IsOwnerPermission])

    def list(self, request, *args, **kwargs):
        user = self.request.user
        filters = {}
        if not user.is_superuser:
            filters = {'username': user.username}
        queryset = self.get_queryset().filter(**filters)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        queryset = self.get_queryset().filter(username=self.request.user)
        if queryset.exists():
            return Response({'detail': 'Object already exists'},
                            status=HTTP_409_CONFLICT)
        content = json.loads(self.request.body.decode("utf-8"))
        queryset = self.get_queryset().filter(directory_id=content['directory_id'])
        if queryset.exists() and self.request.user.username != queryset.all()[0].username:
            c = queryset.first()
            logger.info(f'Bump username : {self.request.user.username} => {c.username}')
            c.username = self.request.user.username
            c.save()
            return Response({'detail': 'Object already exists (login has been updated)'},
                            status=HTTP_409_CONFLICT)
        return super().post(request, *args, **kwargs)
