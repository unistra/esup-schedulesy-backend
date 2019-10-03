import uuid
from functools import partial

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.settings import api_settings

from schedulesy.apps.ade_api.models import LocalCustomization
from schedulesy.apps.ade_api.serializers import LocalCustomizationSerializer
from schedulesy.apps.ade_legacy.views import IsOwnerPermission
from schedulesy.apps.refresh.tasks import (
    bulldoze as resource_bulldoze, refresh_all,
    refresh_resource as resource_task)
from .models import Access, AdeConfig, DisplayType, Resource
from .serializers import (
    AccessSerializer, AdeConfigSerializer, ResourceSerializer)


def refresh(request):  # pragma: no cover
    if request.method == "GET":
        result = refresh_all.delay()
        return JsonResponse(result.get())


def bulldoze(request):  # pragma: no cover
    if request.method == "GET":
        resource_bulldoze.delay()
        return JsonResponse({})


def refresh_resource(request, ext_id):  # pragma: no cover
    resource_task.delay(ext_id, 1, str(uuid.uuid4()))
    return JsonResponse({})


class ResourceDetail(generics.RetrieveAPIView):
    queryset = Resource.objects.all()
    serializer_class = ResourceSerializer
    permission_classes = (permissions.AllowAny,)
    lookup_field = 'ext_id'


class DisplayTypeList(generics.ListAPIView):
    queryset = DisplayType.objects.all()
    permission_classes = (permissions.AllowAny,)

    def list(self, request, *args, **kwargs):
        return Response(self.get_queryset().values_list('name', flat=True))


class AdeConfigDetail(generics.RetrieveAPIView):
    queryset = AdeConfig.objects.all()
    serializer_class = AdeConfigSerializer
    permission_classes = (permissions.AllowAny,)

    def get_object(self):
        obj = get_object_or_404(self.get_queryset(), pk=1)
        self.check_object_permissions(self.request, obj)
        return obj


class AccessDelete(generics.DestroyAPIView):
    queryset = Access.objects.all()
    permission_classes = (
        api_settings.DEFAULT_PERMISSION_CLASSES +
        [partial(IsOwnerPermission, 'customization__username')]
    )

    def get_object(self):
        obj = get_object_or_404(
            self.get_queryset(),
            customization__username=self.kwargs['username'],
            key=self.kwargs['key']
        )
        return obj


class AccessList(generics.ListCreateAPIView):
    queryset = Access.objects.all()
    serializer_class = AccessSerializer
    permission_classes = (
        api_settings.DEFAULT_PERMISSION_CLASSES +
        [partial(IsOwnerPermission, 'customization__username')])

    def get_queryset(self):
        return self.queryset \
            .filter(customization__username=self.kwargs['username'])

    def get_serializer_context(self):
        lc = get_object_or_404(
            LocalCustomization, username=self.kwargs['username'])
        context = super().get_serializer_context()
        context.update({'customization': lc})
        return context


class LocalCustomizationDetail(generics.RetrieveAPIView):
    queryset = LocalCustomization.objects.all()
    serializer_class = LocalCustomizationSerializer
    permission_classes = (
        api_settings.DEFAULT_PERMISSION_CLASSES + [IsOwnerPermission])
    lookup_field = 'username'
