from rest_framework.urlpatterns import format_suffix_patterns
from django.conf.urls import url
from django.urls import path

from . import views

app_name = "api"

urlpatterns = [
    url(r'refresh/$', views.refresh, name='refresh'),
]

ws_urlpatterns = [
    # url(r'resources/$', views.ResourceList.as_view(), name='resources'),
    path('resource/<str:ext_id>', views.ResourceDetail.as_view(), name='resource'),
    path('display_types', views.DisplayTypeList.as_view(), name='display_types'),
]

urlpatterns += format_suffix_patterns(ws_urlpatterns, suffix_required=True)
