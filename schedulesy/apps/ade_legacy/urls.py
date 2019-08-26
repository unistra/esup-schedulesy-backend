from rest_framework.urlpatterns import format_suffix_patterns
from django.conf.urls import url

from . import views

app_name = "legacy"

urlpatterns = [
    url(r'^customization/(?P<username>(\w|.)+)$', views.CustomizationDetailAdmin.as_view(), name='customization-detail-admin'),
    url(r'^customization$', views.CustomizationDetail.as_view(), name='customization-detail'),
    url(r'^customizations$', views.CustomizationList.as_view(), name='customization-list'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
