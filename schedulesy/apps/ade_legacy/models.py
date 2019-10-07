from django.db import models
from django.utils.translation import ugettext_lazy as _

from schedulesy.apps.ade_api.models import LocalCustomization, Resource


class Customization(models.Model):
    id = models.AutoField(primary_key=True, db_column='id')
    display_configuration = models.CharField(
        max_length=60, db_column='configuration_affichage', default='')
    resources = models.CharField(
        max_length=300, db_column='ressources', default='', blank=True)
    directory_id = models.CharField(
        max_length=32, db_column='uds_directory_id')
    rh_id = models.CharField(max_length=15, db_column='code_harp', default='')
    creation_date = models.DateTimeField(
        db_column='date_creation', auto_now_add=True)
    customization_date = models.DateTimeField(
        db_column='date_personnalisation', auto_now=True)
    username = models.CharField(max_length=32, db_column='uid')
    configuration = None

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Saves must be reflected in local customization
        lc, created = LocalCustomization.objects.get_or_create(
            customization_id=self.id,
            defaults={
                'directory_id': self.directory_id,
                'username': self.username,
            }
        )
        lc.configuration = self.configuration
        lc.save()
        resource_ids = (
            set(self.resources.split(",")) if self.resources else set())
        existing_ids = set(lc.resources.values_list('ext_id', flat=True))

        # Removing unselected resources
        lc.resources.remove(
            *(lc.resources.filter(ext_id__in=(existing_ids - resource_ids))))

        # Adding missing resources
        lc.resources.add(*(
            Resource.objects.get_or_create(ext_id=x)[0] for x in
            (resource_ids - existing_ids)))

    class Meta:
        managed = False
        db_table = 'w_edtperso'
        verbose_name = _('Customization')
        verbose_name_plural = _('Customizations')

    def __str__(self):
        return '{0.username}'.format(self)
