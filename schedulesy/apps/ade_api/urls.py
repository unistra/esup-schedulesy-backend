from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from . import views

app_name = "api"

urlpatterns = [
    path('bulldoze/', views.bulldoze, name='bulldoze'),
    path('refresh/', views.refresh, name='refresh'),
    path('refresh/event/<str:ext_id>', views.refresh_event, name='refresh_event'),
    path('refresh/resource/<str:ext_id>', views.refresh_resource, name='refresh_resource'),
    path('sync/', views.sync_customization, name='sync_customization'),

    path('calendar/<str:uuid>/export', views.calendar_export, name='calendar-export'),
]

ws_urlpatterns = [
    path('ade_config', views.AdeConfigDetail.as_view(), name='ade_config'),

    path('customization/<str:username>/uuid/<str:key>',
         views.AccessDelete.as_view(), name='access_delete'),
    path('customization/<str:username>/uuid', views.AccessList.as_view(), name='access_list'),

    path('display_types', views.DisplayTypeList.as_view(), name='display_types'),

    path('resource/<str:ext_id>', views.ResourceDetail.as_view(), name='resource'),
    path('calendar/<str:username>', views.CalendarDetail.as_view(), name='calendar'),
]

urlpatterns += format_suffix_patterns(ws_urlpatterns, suffix_required=True)
