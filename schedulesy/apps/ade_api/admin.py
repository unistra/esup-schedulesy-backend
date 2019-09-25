from django.contrib import admin

from .models import AdeConfig, DisplayType, Fingerprint, Resource, LocalCustomization


@admin.register(AdeConfig, DisplayType, Fingerprint, Resource, LocalCustomization)
class APIAdmin(admin.ModelAdmin):
    pass
