import logging
from datetime import datetime, timedelta
import time

from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.core.files.storage import default_storage
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from ics import Calendar, Event

from schedulesy.libs.decorators import MemoizeWithTimeout
from .utils import generate_uuid, get_ade_timezone


logger = logging.getLogger(__name__)


class Resource(models.Model):
    ext_id = models.CharField(max_length=25, unique=True, db_index=True)
    fields = JSONField(blank=True, null=True)
    parent = models.ForeignKey(
        'self', blank=True, null=True, related_name='children',
        on_delete=models.CASCADE)
    events = JSONField(blank=True, null=True)

    class Meta:
        verbose_name = _('Resource')
        verbose_name_plural = _('Resources')

    def __str__(self):
        return '{0.ext_id}'.format(self)


class Fingerprint(models.Model):
    ext_id = models.CharField(max_length=25)
    method = models.CharField(max_length=50)
    fingerprint = models.CharField(max_length=50)

    class Meta:
        verbose_name = _('Fingerprint')
        verbose_name_plural = _('Fingerprints')

    def __str__(self):
        return '{0.ext_id} - {0.method}'.format(self)


class DisplayType(models.Model):
    name = models.CharField(_('Name'), max_length=256, unique=True)

    class Meta:
        verbose_name = _('Display type')
        verbose_name_plural = _('Display types')

    def __str__(self):
        return '{0.name}'.format(self)


class AdeConfig(models.Model):

    ade_url = models.URLField(_('ADE URL'))
    parameters = JSONField(_('Parameters'))

    class Meta:
        verbose_name = _('ADE config')
        verbose_name_plural = _('ADE config')

    def __str__(self):
        return str(_('ADE config'))

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass


class LocalCustomization(models.Model):
    """
    Local customization. It contains mirror data from the ADE model for
    standalone usage.
    """

    customization_id = models.IntegerField(unique=True)
    directory_id = models.CharField(
        max_length=32, db_column='uds_directory_id')
    username = models.CharField(
        max_length=32, db_column='uid', blank=True, unique=True)
    resources = models.ManyToManyField(Resource)
    configuration = JSONField(blank=True, null=True)

    class Meta:
        verbose_name = _('Local Customization')
        verbose_name_plural = _('Local Customizations')

    def __str__(self):
        return '{0.username}'.format(self)

    @property
    def ics_calendar_filename(self):
        return f'{self.username}.ics'

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        # import schedulesy.apps.refresh.tasks
        # schedulesy.apps.refresh.tasks.generate_ics.delay(self.id, order_time=time.time())
        if is_new:
            Access.objects.create(name=self.username, customization=self)

    @cached_property
    def events(self):
        """
        Merges all events
        :return:
        """
        def get_event_type(t):
            return (x.events[t] for x in resources
                    if x.events and t in x.events)

        resources = self.resources.all()
        if len(resources) == 0:
            return {}
        if len(resources) == 1:
            return resources[0].events or {}

        events = {l['id']: l for l in
                  (item for sl in get_event_type('events') for item in sl)}
        result = {'events': events.values()}

        for rt in ('trainees', 'instructors', 'classrooms'):
            result[rt] = (
                {k: v for d in get_event_type(rt) for k, v in d.items()})
        return result

    def generate_ics_calendar(self):
        logger.debug(f"Refreshed ICS for {self.username}")

        @MemoizeWithTimeout()
        def format_ics_date(event_date):
            return get_ade_timezone().localize(
                datetime.strptime(event_date, '%d/%m/%Y %H:%M'))

        def format_ics_location(classroom):
            return f'{classroom["name"]} ({", ".join(classroom["genealogy"])})'

        def format_geolocation(classrooms):
            try:
                # Returns the first geolocation found
                return next(filter(
                    None, (c.get('geolocation') for c in classrooms)))[:2]
            except Exception:
                return None

        # @MemoizeWithTimeout()
        # def replace(date, offset):
        #     return date.replace(
        #         minutes=+(offset * settings.ADE_DEFAULT_DURATION))

        def format_description(resources):
            descriptions = []
            # TODO: i18n ?
            for key, display in {'trainees': 'Filières',
                                 'instructors': 'Intervenants',
                                 'category5': 'Matières'}.items():
                if key in resources:
                    descriptions.append(
                        f'{display} : ' +
                        ','.join([x['name'] for x in resources[key]]))
            return ','.join(descriptions)

        merged_events = self.events
        events = merged_events.get('events', [])
        res_list = ('classrooms', 'trainees', 'instructors', 'category5')
        if events:
            calendar = Calendar()
            size = len(events)

            if size < settings.ADE_MAX_EVENTS:
                for event in events:
                    resources = {r: [v for k, v in merged_events.get(r, {}).items()
                                 if k in event.get(r)]
                             for r in res_list if r in event.keys()}
                    classrooms = resources.get('classrooms', ())
                    begin_time = format_ics_date(
                        f'{event["date"]} {event["startHour"]}')

                    # Genereate ICS event
                    e = Event()
                    e.name = event['name']
                    e.begin = begin_time
                    e.end = begin_time + timedelta(
                        minutes=(int(event["duration"]) * settings.ADE_DEFAULT_DURATION))
                    e.geo = format_geolocation(classrooms)
                    e.location = ';'.join(map(format_ics_location, classrooms))
                    # e.last_modified = event['lastUpdate']
                    e.description = format_description(resources)
                    calendar.events.add(e)
            else:
                logger.error(f'Too much events for {self.username} : {size}')
                e = Event()
                e.name = "Votre calendrier dépasse le nombre d'événements autorisé"
                e.begin = datetime.strptime('01/01/2000 00:00', '%d/%m/%Y %H:%M')
                e.end = datetime.strptime('01/01/2100 00:00', '%d/%m/%Y %H:%M')
                calendar.events.add(e)

            with default_storage.open(self.ics_calendar_filename, 'w') as fh:
                fh.write(str(calendar))


class Access(models.Model):

    key = models.CharField(
        max_length=36, unique=True, default=generate_uuid)
    creation_date = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=256)
    customization = models.ForeignKey(
        'ade_api.LocalCustomization', related_name='accesses',
        on_delete=models.CASCADE)

    class Meta:
        verbose_name = _('Access')
        verbose_name_plural = _('Accesses')
        unique_together = ('name', 'customization')

    def __str__(self):
        return '{0.key} ({0.name})'.format(self)

    @property
    def is_last_access(self):
        return not self.customization.accesses.count() > 1

    def delete(self, *args, **kwargs):
        if not self.is_last_access:
            super().delete(*args, **kwargs)
