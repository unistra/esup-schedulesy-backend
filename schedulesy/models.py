from django.contrib.postgres.fields import JSONField
from django.db import models


class Resource(models.Model):
    ext_id = models.CharField(max_length=25, unique=True, db_index=True)
    fields = JSONField()
