from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from .views import home

admin.autodiscover()

urlpatterns = [
    # Examples:
    path('', home, name='home'),
    path('accounts/', include('django_cas.urls', namespace='django_cas')),
    path('api/', include('schedulesy.apps.ade_api.urls', namespace='api')),
    path('legacy/', include('schedulesy.apps.ade_legacy.urls', namespace='legacy')),

    path('admin/', admin.site.urls),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# debug toolbar for dev
if settings.DEBUG and 'debug_toolbar'in settings.INSTALLED_APPS:
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]

# Must be the last url
urlpatterns += [
    url(r'^.*$', home, name='home'),
]
