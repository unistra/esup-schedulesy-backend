from rest_framework.urlpatterns import format_suffix_patterns
from django.conf.urls import url
from django.urls import path

from . import views

app_name = "api"

urlpatterns = [
    url(r'refresh/$', views.refresh, name='refresh'),
    url(r'bulldoze/$', views.bulldoze, name='bulldoze'),
    path('refresh/resource/<str:ext_id>', views.refresh_resource, name='refresh_resource'),
]

ws_urlpatterns = [
    # url(r'resources/$', views.ResourceList.as_view(), name='resources'),
    path('resource/<str:ext_id>', views.ResourceDetail.as_view(), name='resource'),
    path('display_types', views.DisplayTypeList.as_view(), name='display_types'),
    path('ade_config', views.AdeConfigDetail.as_view(), name='ade_config'),
    path('calendar/<str:username>', views.LocalCustomizationDetail.as_view(), name='calendar'),
]

urlpatterns += format_suffix_patterns(ws_urlpatterns, suffix_required=True)
