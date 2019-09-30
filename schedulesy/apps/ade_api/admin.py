from django.contrib import admin

from .models import (AdeConfig, DisplayType, Fingerprint, LocalCustomization,
                     Resource)


@admin.register(DisplayType, Fingerprint, LocalCustomization, Resource)
class APIAdmin(admin.ModelAdmin):
    pass


@admin.register(AdeConfig)
class AdeConfigAdmin(admin.ModelAdmin):

    def has_add_permission(self, request, obj=None):
        return False
