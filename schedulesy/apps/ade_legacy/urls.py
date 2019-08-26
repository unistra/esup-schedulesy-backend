from rest_framework.urlpatterns import format_suffix_patterns
from django.conf.urls import url
from django.urls import path

from . import views

app_name = "legacy"

urlpatterns = [
    url(r'^wedtperso/(?P<pk>\w+)$', views.WEdtpersoDetail.as_view(), name='wedtperso-all-detail'),
    url(r'^wedtperso$', views.WEdtpersoList.as_view(), name='wedtperso-all-list'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
