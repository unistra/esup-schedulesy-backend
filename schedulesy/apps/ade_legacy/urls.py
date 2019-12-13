from django.urls import path, re_path
from rest_framework.urlpatterns import format_suffix_patterns

from . import views

app_name = "legacy"

urlpatterns = [
    re_path(r'^customization/(?P<username>[\w.\-]+)$', views.CustomizationDetail.as_view(), name='customization-detail'),
    path('customization', views.CustomizationList.as_view(), name='customization-list'),
]

urlpatterns = format_suffix_patterns(urlpatterns, suffix_required=True)
