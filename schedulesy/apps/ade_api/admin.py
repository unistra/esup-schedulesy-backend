from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from .models import (
    Access,
    AdeConfig,
    DisplayType,
    Fingerprint,
    LocalCustomization,
    Resource,
)


class AccessInline(admin.StackedInline):
    model = Access
    extra = 0


@admin.register(DisplayType, Fingerprint, Resource)
class APIAdmin(admin.ModelAdmin):
    pass


@admin.register(Access)
class AccessAdmin(admin.ModelAdmin):
    search_fields = ('key', 'customization__username')
    list_display = (
        '__str__',
        'customization_username',
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('customization')

    def customization_username(self, obj):
        return obj.customization.username

    customization_username.short_description = _('Username')


@admin.register(AdeConfig)
class AdeConfigAdmin(admin.ModelAdmin):
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(LocalCustomization)
class LocalCustomizationAdmin(admin.ModelAdmin):
    inlines = (AccessInline,)
