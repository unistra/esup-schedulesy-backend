from datetime import datetime

from django.contrib.postgres.fields import JSONField
from django.core.files.storage import default_storage
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from ics import Calendar, Event

from .utils import generate_uuid


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

    @cached_property
    def events(self):
        """
        Merges all events
        :return:
        """
        def get_event_type(t):
            return (x.events[t] for x in resources if t in x.events)

        resources = self.resources.all()
        if len(resources) == 0:
            return {}
        if len(resources) == 1:
            return resources[0].events

        events = {l['id']: l for l in
                  (item for sl in get_event_type('events') for item in sl)}
        result = {'events': events.values()}

        for rt in ('trainees', 'instructors', 'classrooms'):
            result[rt] = (
                {k: v for d in get_event_type(rt) for k, v in d.items()})
        return result

    def generate_ics_calendar(self):

        def format_ics_date(event_date):
            return datetime.strptime(event_date, '%d/%m/%Y %H:%M')

        def format_ics_location(classroom):
            return f'{classroom["name"]} ({", ".join(classroom["genealogy"])})'

        merged_events = self.events
        events = merged_events.get('events', [])
        if events:
            classrooms = merged_events['classrooms']
            calendar = Calendar()
            for event in events:
                e = Event()
                e.name = event['name']
                e.begin = format_ics_date(
                    f'{event["date"]} {event["endHour"]}')
                e.duration = float(event['duration'])
                e.location = ', '.join(format_ics_location(classrooms[cl])
                                       for cl in event['classrooms'])
                # e.last_modified = event['lastUpdate']
                calendar.events.add(e)

            with default_storage.open(self.ics_calendar_filename, 'w') as fh:
                fh.writelines(calendar)


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
