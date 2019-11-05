import logging
import uuid
from functools import partial

from django.contrib.auth.decorators import user_passes_test
from django.core.files.storage import default_storage
from django.http import FileResponse, Http404, JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.settings import api_settings

from schedulesy.apps.ade_legacy.models import Customization
from schedulesy.apps.refresh.tasks import (
    bulldoze as resource_bulldoze, refresh_all,
    refresh_resource as resource_task)
from schedulesy.libs.permissions import IsOwnerPermission
from .models import (
    Access, AdeConfig, LocalCustomization, DisplayType, Resource)
from .serializers import (
    AccessSerializer, AdeConfigSerializer, CalendarSerializer,
    ResourceSerializer)

logger = logging.getLogger(__name__)


@user_passes_test(lambda u: u.is_superuser, login_url='/')
def bulldoze(request):  # pragma: no cover
    if request.method == "GET":
        resource_bulldoze.delay()
        return JsonResponse({})


@user_passes_test(lambda u: u.is_superuser, login_url='/')
def refresh(request):  # pragma: no cover
    if request.method == "GET":
        result = refresh_all.delay()
        return JsonResponse(result.get())


@user_passes_test(lambda u: u.is_superuser, login_url='/')
def refresh_event(request, ext_id):  # pragma: no cover
    # http://localhost:8000/api/refresh/event/1?resources=2&resources=3
    resources = request.GET.get('resources')
    resource_task.delay(ext_id, resources, 1, str(uuid.uuid4()))
    return JsonResponse({})


@user_passes_test(lambda u: u.is_superuser, login_url='/')
def sync_customization(request):
    customizations = Customization.objects.all()
    local_customizations = LocalCustomization.objects.all()
    missing = 0
    for c in [x for x in customizations if x.username not in [x.username for x in local_customizations]]:
        try:
            missing += 1
            c._sync()
        except Exception as e:
            logger.error(e)
    for lc in [x for x in local_customizations if x.ext_id not in [x.id for x in customizations]]:
        try:
            logger.warning(f'Deleting local customization for {lc.username} (missing matching customization)')
            lc.delete()
        except Exception as e:
            logger.error(e)
    return JsonResponse({"Created": missing, "Total": len(customizations)})


def calendar_export(request, username):
    lc = get_object_or_404(LocalCustomization, username=username)
    try:
        return FileResponse(
            default_storage.open(lc.ics_calendar_filename),
            as_attachment=True,
            content_type='text/calendar'
        )
    except Exception:
        raise Http404()


@user_passes_test(lambda u: u.is_superuser, login_url='/')
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


class CalendarDetail(generics.RetrieveAPIView):
    queryset = LocalCustomization.objects.all()
    serializer_class = CalendarSerializer
    permission_classes = (
            api_settings.DEFAULT_PERMISSION_CLASSES + [IsOwnerPermission])
    lookup_field = 'username'
