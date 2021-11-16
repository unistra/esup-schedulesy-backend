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
from ..ade_api.models import LocalCustomization, Access

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

        def username_changed():
            content = json.loads(self.request.body.decode("utf-8"))
            qs = self.get_queryset().filter(directory_id=content['directory_id'])
            changed = qs.exists() and self.request.user.username != qs.all()[0].username
            if changed:
                c = qs.first()
                old = c.username
                logger.info(f'Bump username : {self.request.user.username} => {old}')
                c.username = self.request.user.username
                c.save()
                print(f'C {c.username}')
                for lc in LocalCustomization.objects.filter(username=old).all():
                    lc.username = self.request.user.username
                    lc.save()
                    print(f'LC {lc.username}')
                for a in Access.objects.filter(name=old).all():
                    a.name = self.request.user.username
                    a.save()
                    print(f'A {a.name}')
            return changed

        if username_changed():
            return Response({'detail': 'Object already exists (login has been updated)'},
                            status=HTTP_409_CONFLICT)

        return super().post(request, *args, **kwargs)
