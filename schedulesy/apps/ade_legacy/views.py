from uuid import uuid4

from django.contrib.auth.models import User
from rest_framework.generics import RetrieveUpdateDestroyAPIView, ListCreateAPIView
from rest_framework_simplejwt.tokens import AccessToken

from . import models
from . import serializers


class CustomizationDetail(RetrieveUpdateDestroyAPIView):
    queryset = models.Customization.objects.all()
    serializer_class = serializers.WEdtpersoSerializer
    lookup_field = 'username'

    def perform_authentication(self, request):
        meta = request.META
        if 'HTTP_AUTHORIZATION' in meta and meta['HTTP_AUTHORIZATION'].startswith('Bearer '):
            t = meta['HTTP_AUTHORIZATION'].split()[1]
            try:
                # Will create user if token is valid
                token = AccessToken(t)
                t_user = User.objects.get_or_create(username=token.get('user_id'),
                                           defaults={'is_active': True})
                if t_user[1]:
                    t_user[0].set_password(str(uuid4()))
                    t_user[0].save()
            except Exception as e:
                # Other controls will be made by call to super method
                pass
        super().perform_authentication(request)


class CustomizationList(ListCreateAPIView):
    queryset = models.Customization.objects.all()
    serializer_class = serializers.WEdtpersoSerializer
