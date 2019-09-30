from rest_framework.urlpatterns import format_suffix_patterns
from django.conf.urls import url
from django.urls import path

from . import views

app_name = "api"

urlpatterns = [
    url(r'refresh/$', views.refresh, name='refresh'),
    path('refresh/resource/<str:ext_id>', views.refresh_resource, name='refresh_resource'),
]

ws_urlpatterns = [
    path('ade_config', views.AdeConfigDetail.as_view(), name='ade_config'),

    path('customization/<str:username>/uuid/<str:key>',
         views.AccessDelete.as_view(), name='access_delete'),
    path('customization/<str:username>/uuid', views.AccessList.as_view(), name='access_list'),

    path('display_types', views.DisplayTypeList.as_view(), name='display_types'),

    path('resource/<str:ext_id>', views.ResourceDetail.as_view(), name='resource'),
]

urlpatterns += format_suffix_patterns(ws_urlpatterns, suffix_required=True)
