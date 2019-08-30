from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils.translation import ugettext_lazy as _


class Resource(models.Model):
    ext_id = models.CharField(max_length=25, unique=True, db_index=True)
    fields = JSONField()


class Fingerprint(models.Model):
    ext_id = models.CharField(max_length=25)
    method = models.CharField(max_length=50)
    fingerprint = models.CharField(max_length=50)


class DisplayType(models.Model):
    name = models.CharField(_('Name'), max_length=256, unique=True)

    class Meta:
        verbose_name = _('Display type')
        verbose_name_plural = _('Display types')

    def __str__(self):
        return '{0.name}'.format(self)
