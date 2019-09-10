from django.contrib import admin

from .models import AdeConfig, DisplayType, Fingerprint, Resource


@admin.register(AdeConfig, DisplayType, Fingerprint, Resource)
class APIAdmin(admin.ModelAdmin):
    pass
