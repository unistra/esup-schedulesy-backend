from django.contrib import admin

from .models import DisplayType, Fingerprint, Resource


@admin.register(DisplayType, Fingerprint, Resource)
class APIAdmin(admin.ModelAdmin):
    pass
