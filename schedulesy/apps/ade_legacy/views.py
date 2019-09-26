from rest_framework import permissions
from rest_framework.generics import (
    ListCreateAPIView, RetrieveUpdateDestroyAPIView)
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.status import HTTP_409_CONFLICT

from schedulesy.apps.ade_legacy.serializers import CustomizationSerializer
from . import models


class IsOwnerPermission(permissions.BasePermission):
    """Object-level permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        return obj.username == request.user.username


class CustomizationDetail(RetrieveUpdateDestroyAPIView):

    permission_classes = api_settings.DEFAULT_PERMISSION_CLASSES +\
        [IsOwnerPermission]
    queryset = models.Customization.objects.all()
    serializer_class = CustomizationSerializer
    lookup_field = 'username'


class CustomizationList(ListCreateAPIView):
    queryset = models.Customization.objects.all()
    serializer_class = CustomizationSerializer
    permission_classes = (IsOwnerPermission,)

    def list(self, request, *args, **kwargs):
        user = self.request.user
        filters = {}
        if not user.is_superuser:
            filters = {'username': user.username}
        queryset = self.get_queryset().filter(**filters)
        serializer = CustomizationSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        filters = {'username': self.request.user}
        queryset = self.get_queryset().filter(**filters)
        if queryset.exists():
            return Response({'detail': 'Object already exists'},
                            status=HTTP_409_CONFLICT)
        return super().post(request, *args, **kwargs)
