import calendar
import datetime
import logging
import time
import uuid
from functools import partial

from django.conf import settings
from django.contrib.auth.decorators import user_passes_test
from django.core.files.storage import default_storage
from django.http import FileResponse, Http404, JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.settings import api_settings

from schedulesy.apps.ade_legacy.models import Customization
from schedulesy.apps.refresh.tasks import bulldoze as resource_bulldoze
from schedulesy.apps.refresh.tasks import do_refresh_all_events, refresh_all
from schedulesy.apps.refresh.tasks import refresh_resource as resource_task
from schedulesy.libs.permissions import IsOwnerPermission

from ...libs.decorators import refresh_if_necessary
from .exception import SearchTooWideError, TooMuchEventsError
from .models import Access, AdeConfig, DisplayType, LocalCustomization, Resource
from .refresh import Refresh
from .queries import get_hierarchical_classrooms_by_depth, get_trainees_size
from .serializers import (
    AccessSerializer,
    AdeConfigSerializer,
    BuildingSerializer,
    CalendarSerializer,
    EventsSerializer,
    InfoSerializer,
    ResourceSerializer,
)

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
def refresh_all_events(request):  # pragma: no cover
    count = do_refresh_all_events()
    return JsonResponse({'message': f'Ordered refresh of {count} ressources'})


@user_passes_test(lambda u: u.is_superuser, login_url='/')
def sync_customization(request):
    customizations = Customization.objects.values_list('id', flat=True)
    lcl = LocalCustomization.objects.values_list('customization_id', flat=True)

    deleting = 0
    for lc in (x for x in lcl if x not in customizations):
        try:
            lc = LocalCustomization.objects.get(customization_id=lc)
            logger.debug(
                f'Deleting local customization for {lc.username} (missing matching customization)'
            )
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

    return JsonResponse(
        {"Created": missing, "Deleted": deleting, "Total": len(customizations)}
    )


def calendar_export(request, uuid):
    lc = get_object_or_404(LocalCustomization, accesses__key=uuid)
    filename = lc.ics_calendar_filename

    class ExpiredFileError(Exception):
        pass

    def file_response():
        if not default_storage.exists(filename):
            raise FileNotFoundError
        if (
            time.time() - default_storage.get_modified_time(filename).timestamp()
            > settings.ICS_EXPIRATION
        ):
            raise ExpiredFileError
        response = FileResponse(
            default_storage.open(filename),
            as_attachment=True,
            content_type='text/calendar',
            filename=f'{lc.username}.ics',
        )
        response.setdefault('Content-Length', default_storage.size(filename))
        return response

    try:
        return file_response()
    except (FileNotFoundError, OSError, ExpiredFileError):
        try:
            # Generate the ICS if it does not exist
            logger.debug("Regenerated file")
            lc.generate_ics_calendar(filename=filename)
            return file_response()
        except Exception:
            raise Http404()
    except Exception:
        raise Http404()


@user_passes_test(lambda u: u.is_superuser, login_url='/')
def refresh_resource(request, ext_id):  # pragma: no cover
    logger.debug(ext_id)
    resource_task.delay(ext_id, 1, str(uuid.uuid4()))
    return JsonResponse({})


class ResourceDetail(generics.RetrieveAPIView):
    queryset = Resource.objects.all()
    serializer_class = ResourceSerializer
    permission_classes = (permissions.IsAuthenticated,)
    lookup_field = 'ext_id'


class EventsDetail(generics.RetrieveAPIView):
    queryset = Resource.objects.all()
    serializer_class = EventsSerializer
    lookup_field = 'ext_id'
    permission_classes = (permissions.AllowAny,)


class InstructorDetail(generics.ListAPIView):
    serializer_class = ResourceSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        """
        Optionally restricts the returned purchases to a given user,
        by filtering against a `username` query parameter in the URL.
        """
        queryset = Resource.objects.all()
        email = self.request.query_params.get('email', None)
        if email is not None:
            queryset = queryset.filter(fields__email=email)
            return queryset
        raise SearchTooWideError


class DisplayTypeList(generics.ListAPIView):
    queryset = DisplayType.objects.all()
    permission_classes = (permissions.IsAuthenticated,)

    def list(self, request, *args, **kwargs):
        return Response(self.get_queryset().values_list('name', flat=True))


class AdeConfigDetail(generics.RetrieveAPIView):
    queryset = AdeConfig.objects.all()
    serializer_class = AdeConfigSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        obj = get_object_or_404(self.get_queryset(), pk=1)
        self.check_object_permissions(self.request, obj)
        return obj


class AccessDeletePermission(permissions.BasePermission):
    """Check permissions for accesses deletion"""

    message = _('A customization must always have at least one access')

    def has_object_permission(self, request, view, obj):
        return not obj.is_last_access


class AccessDelete(generics.DestroyAPIView):
    queryset = Access.objects.all()
    permission_classes = api_settings.DEFAULT_PERMISSION_CLASSES + [
        partial(IsOwnerPermission, 'customization__username'),
        AccessDeletePermission,
    ]

    def get_object(self):
        obj = get_object_or_404(
            self.get_queryset(),
            customization__username=self.kwargs['username'],
            key=self.kwargs['key'],
        )
        self.check_object_permissions(self.request, obj)
        return obj


class AccessList(generics.ListCreateAPIView):
    queryset = Access.objects.all()
    serializer_class = AccessSerializer
    permission_classes = api_settings.DEFAULT_PERMISSION_CLASSES + [
        partial(IsOwnerPermission, 'customization__username')
    ]

    def get_queryset(self):
        return self.queryset.filter(customization__username=self.kwargs['username'])

    def get_serializer_context(self):
        lc = get_object_or_404(LocalCustomization, username=self.kwargs['username'])
        context = super().get_serializer_context()
        context.update({'customization': lc})
        return context


class CalendarDetail(generics.RetrieveAPIView):
    queryset = LocalCustomization.objects.all()
    serializer_class = CalendarSerializer
    permission_classes = api_settings.DEFAULT_PERMISSION_CLASSES + [IsOwnerPermission]
    lookup_field = 'username'

    def get(self, request, *args, **kwargs):
        try:
            return super().get(request, *args, **kwargs)
        except TooMuchEventsError as e:
            return JsonResponse(e.context(), status=413)


class InfoDetail(generics.RetrieveAPIView):
    queryset = LocalCustomization.objects.all()
    serializer_class = InfoSerializer
    permission_classes = (permissions.IsAdminUser,)
    lookup_field = 'username'


class PublicViewMixin:
    authentication_classes = []
    permission_classes = (permissions.AllowAny,)


class BuildingList(PublicViewMixin, generics.ListAPIView):
    serializer_class = BuildingSerializer

    def get_queryset(self):
        return get_hierarchical_classrooms_by_depth(depth=3)


class BuildingAttendanceList(PublicViewMixin, generics.ListAPIView):

    def _generate_hours(self, start=8, end=18, step=15):
        t = datetime.date.today()
        month, year = t.month, t.year
        smonth = str(t.month).zfill(2)
        hms = ['{:0>2}:{:0>2}'.format(h, m) for h in range(start, end)
               for m in range(0, 60, step)]
        dts = {}
        for day in (str(d).zfill(2) for w in calendar.monthcalendar(year, month)
                    for d in w[:-2] if d):
            for hm in hms:
                dts[f'{day}/{smonth}/{year} {hm}'] = 0
        return dts

    def list(self, request, building_id, *args, **kwargs):

        # Check if the classroom has the correct depth
        if not building_id in (c['id'] for c in get_hierarchical_classrooms_by_depth(depth=3)):
            return Response(status=status.HTTP_403_FORBIDDEN)

        trainees_dict = {t['ext_id']: t['size'] for t in get_trainees_size()}
        classroom = Resource.objects.get(pk=building_id)
        result = self._generate_hours()
        for event in classroom.events.get('events', []):
            ds = f"{event['date']} {event['startHour']}"
            result[ds] = sum(
                trainees_dict.get(t, 0) for t in event.get('trainees', []))
        return JsonResponse(result)
