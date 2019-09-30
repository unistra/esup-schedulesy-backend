import uuid

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions
from rest_framework.response import Response

from schedulesy.apps.ade_api.models import LocalCustomization
from schedulesy.apps.ade_api.serializers import LocalCustomizationSerializer
from schedulesy.apps.refresh.tasks import refresh_resource as resource_task, refresh_all, bulldoze as resource_bulldoze
from .models import AdeConfig, DisplayType, Resource
from .serializers import AdeConfigSerializer, ResourceSerializer


def refresh(request):
    if request.method == "GET":
        result = refresh_all.delay()
        return JsonResponse(result.get())


def bulldoze(request):
    if request.method == "GET":
        result = resource_bulldoze.delay()
        return JsonResponse({})


def refresh_resource(request, ext_id):
    resource_task.delay(ext_id, 1, str(uuid.uuid4()))
    return JsonResponse({})


class ResourceDetail(generics.RetrieveAPIView):
    queryset = Resource.objects.all()
    serializer_class = ResourceSerializer
    permission_classes = (permissions.AllowAny, )
    lookup_field = 'ext_id'


class DisplayTypeList(generics.ListAPIView):
    queryset = DisplayType.objects.all()
    permission_classes = (permissions.AllowAny, )

    def list(self, request, *args, **kwargs):
        return Response(self.get_queryset().values_list('name', flat=True))


class AdeConfigDetail(generics.RetrieveAPIView):
    queryset = AdeConfig.objects.all()
    serializer_class = AdeConfigSerializer
    permission_classes = (permissions.AllowAny, )

    def get_object(self):
        obj = get_object_or_404(self.get_queryset(), pk=1)
        self.check_object_permissions(self.request, obj)
        return obj

class LocalCustomizationDetail(generics.RetrieveAPIView):
    queryset = LocalCustomization.objects.all()
    serializer_class = LocalCustomizationSerializer
    permission_classes = (permissions.AllowAny, )
    lookup_field = 'username'