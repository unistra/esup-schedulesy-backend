import logging
import uuid
from functools import partial

from django.contrib.auth.decorators import user_passes_test
from django.core.files.storage import default_storage
from django.db.models.expressions import RawSQL
from django.http import FileResponse, Http404, JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
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
    customizations = Customization.objects.values_list('id', flat=True)
    lcl = LocalCustomization.objects.values_list('customization_id', flat=True)

    deleting = 0
    for lc in (x for x in lcl if x not in customizations):
        try:
            lc = LocalCustomization.objects.get(customization_id=lc)
            logger.debug(f'Deleting local customization for {lc.username} (missing matching customization)')
            lc.delete()
            deleting += 1
        except Exception as e:
            logger.error(e)

    missing = 0
    for c in (x for x in customizations if x not in lcl):
        try:
            missing += 1
            customization = Customization.objects.get(id=c)
            logger.debug(f'Creating missing mirror {customization.username}')
            customization._sync()
        except Exception as e:
            logger.error(e)

    return JsonResponse({"Created": missing,
                         "Deleted": deleting,
                         "Total": len(customizations)})


def calendar_export(request, uuid):
    lc = get_object_or_404(LocalCustomization, accesses__key=uuid)
    filename = lc.ics_calendar_filename

    def file_response():
        return FileResponse(
            default_storage.open(filename),
            as_attachment=True,
            content_type='text/calendar',
            filename=f'{lc.username}.ics')

    try:
        return file_response()
    except FileNotFoundError as fnfe:
        try:
            # Generate the ICS if it does not exist
            lc.generate_ics_calendar(filename=filename)
            return file_response()
        except Exception as e:
            raise Http404()
    except Exception:
        raise Http404()


@user_passes_test(lambda u: u.is_superuser, login_url='/')
def refresh_resource(request, ext_id):  # pragma: no cover
    resource_task.delay(ext_id, 1, str(uuid.uuid4()))
    return JsonResponse({})


class ResourceDetail(generics.RetrieveAPIView):
    queryset = Resource.objects\
        .annotate(nb_events=RawSQL("jsonb_array_length(events->'events')", ()))
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


class AccessDeletePermission(permissions.BasePermission):
    """Check permissions for accesses deletion
    """
    message = _('A customization must always have at least one access')

    def has_object_permission(self, request, view, obj):
        return not obj.is_last_access


class AccessDelete(generics.DestroyAPIView):
    queryset = Access.objects.all()
    permission_classes = (
        api_settings.DEFAULT_PERMISSION_CLASSES + [
            partial(IsOwnerPermission, 'customization__username'),
            AccessDeletePermission
        ]
    )

    def get_object(self):
        obj = get_object_or_404(
            self.get_queryset(),
            customization__username=self.kwargs['username'],
            key=self.kwargs['key']
        )
        self.check_object_permissions(self.request, obj)
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
