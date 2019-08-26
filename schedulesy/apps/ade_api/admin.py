from django.contrib import admin

# Register your models here.
from schedulesy.apps.ade_api.models import Resource, Fingerprint


@admin.register(Resource, Fingerprint)
class APIAdmin(admin.ModelAdmin):
    pass
