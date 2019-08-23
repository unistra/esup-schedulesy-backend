from rest_framework.urlpatterns import format_suffix_patterns
from django.conf.urls import url
from django.urls import path

from . import views

app_name = "api"

urlpatterns = [
    url(r'refresh/$', views.refresh, name='refresh'),
    # url(r'resources/$', views.ResourceList.as_view(), name='resources'),
    path('resource/<str:ext_id>', views.ResourceDetail.as_view(), name='resource'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
