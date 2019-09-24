from django.db import models
from django.utils.translation import ugettext_lazy as _


# Create your models here.
from schedulesy.apps.ade_api.models import LocalCustomization, Resource


class Customization(models.Model):
    id = models.AutoField(primary_key=True, db_column='id')
    display_configuration = models.CharField(max_length=60, db_column='configuration_affichage', blank=True)
    resources = models.CharField(max_length=300, db_column='ressources', blank=True)
    directory_id = models.CharField(max_length=32, db_column='uds_directory_id')
    rh_id = models.CharField(max_length=15, db_column='code_harp', blank=True)
    creation_date = models.DateTimeField(db_column='date_creation', blank=True, null=True, auto_now_add=True)
    customization_date = models.DateTimeField(db_column='date_personnalisation', blank=True, null=True, auto_now=True)
    username = models.CharField(max_length=32, db_column='uid', blank=True)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super().save(force_insert, force_update, using, update_fields)
        # Saves must be reflected in local customization
        lc, created = LocalCustomization.objects.get_or_create(customization_id=self.id)
        lc.directory_id = self.directory_id
        lc.username = self.username
        lc.save()
        resource_ids = self.resources.split(",")
        # Removing unselected resources
        for resource in [x for x in lc.resources.all() if x.ext_id not in resource_ids]:
            lc.resources.remove(resource)
        # Adding missing resources
        for id in [x for x in resource_ids if x not in [x.ext_id for x in lc.resources.all()]]:
            resource = Resource.objects.get(ext_id=id)
            lc.resources.add(resource)
        lc.save()

    class Meta:
        managed = False
        db_table = 'w_edtperso'
        verbose_name = _('Customization')
        verbose_name_plural = _('Customizations')

    def __str__(self):
        return '{0.username}'.format(self)
