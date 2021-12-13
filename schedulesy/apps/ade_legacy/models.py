from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from schedulesy.apps.ade_api import models as api


class Customization(models.Model):
    id = models.AutoField(primary_key=True, db_column='id')
    display_configuration = models.CharField(
        max_length=60, db_column='configuration_affichage', default=''
    )
    resources = models.CharField(
        max_length=300, db_column='ressources', default='', blank=True
    )
    directory_id = models.CharField(
        max_length=32, db_column='uds_directory_id', unique=True
    )
    rh_id = models.CharField(max_length=15, db_column='code_harp', default='')
    creation_date = models.DateTimeField(db_column='date_creation', auto_now_add=True)
    customization_date = models.DateTimeField(
        db_column='date_personnalisation', auto_now=True
    )
    username = models.CharField(max_length=32, db_column='uid')
    configuration = None

    @property
    def ics_calendar(self):
        return self.local_customization.ics_calendar_filename

    @cached_property
    def local_customization(self):
        try:
            lc = api.LocalCustomization.objects.get(customization_id=self.id)
            if lc.resources.count() <= 0:
                self._sync()
            return lc
        except api.LocalCustomization.DoesNotExist:
            try:
                # Fixes inconsistency between databases
                lc = api.LocalCustomization.objects.get(username=self.username)
                lc.customization_id = self.id
                lc.save()
                if lc.resources.count() <= 0:
                    self._sync()
                return lc
            except api.LocalCustomization.DoesNotExist:
                return self._sync()

    # TODO: atomic
    def save(self, *args, **kwargs):
        # fix list of resources
        if self.resources != '':
            resources = api.Resource.objects.filter(
                ext_id__in=set(self.resources.split(','))
            )
            self.resources = ','.join([f'{r.ext_id}' for r in resources])
        super().save(*args, **kwargs)
        self._sync()

    def _sync(self):
        # Saves must be reflected in local customization
        lc, created = api.LocalCustomization.objects.get_or_create(
            customization_id=self.id,
            defaults={
                'directory_id': self.directory_id,
                'username': self.username,
            },
        )
        if self.configuration is not None:
            lc.configuration = self.configuration
        lc.save()
        resource_ids = set(self.resources.split(",")) if self.resources else set()
        existing_ids = set(lc.resources.values_list('ext_id', flat=True))

        # Removing unselected resources
        lc.resources.remove(
            *(lc.resources.filter(ext_id__in=(existing_ids - resource_ids)))
        )

        # Adding missing resources
        error = False
        for r_id in resource_ids - existing_ids:
            try:
                r = api.Resource.objects.get(ext_id=r_id)
                lc.resources.add(r)
            except ObjectDoesNotExist:
                # Missing resource, probably deleted by synchronization
                error = True
        if error:
            self.resources = ','.join(lc.resources.values_list('ext_id', flat=True))
        return lc

    class Meta:
        managed = False
        db_table = 'w_edtperso'
        verbose_name = _('Customization')
        verbose_name_plural = _('Customizations')

    def __str__(self):
        return f'{self.username}'
