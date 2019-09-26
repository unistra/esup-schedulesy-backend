from django.contrib import admin

from .models import (AdeConfig, DisplayType, Fingerprint, LocalCustomization,
                     Resource)


@admin.register(AdeConfig, DisplayType, Fingerprint, Resource,
                LocalCustomization)
class APIAdmin(admin.ModelAdmin):
    pass
