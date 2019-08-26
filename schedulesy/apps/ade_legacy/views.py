from uuid import uuid4

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import permissions
from rest_framework.generics import RetrieveUpdateDestroyAPIView, ListCreateAPIView
from rest_framework.response import Response
from rest_framework.status import HTTP_404_NOT_FOUND
from rest_framework_simplejwt.tokens import AccessToken

from schedulesy.apps.ade_legacy.serializers import CustomizationSerializer
from . import models


class CustomizationDetail(RetrieveUpdateDestroyAPIView):
    queryset = models.Customization.objects.all()
    serializer_class = CustomizationSerializer
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

    def get(self, request, *args, **kwargs):
        try:
            obj = self.queryset.get(username=request.user.username)
        except ObjectDoesNotExist:
            return Response(status=HTTP_404_NOT_FOUND, data={'error': 'not found'})
        serializer = CustomizationSerializer(obj, context={'request': request})
        return Response(serializer.data)


class CustomizationDetailAdmin(RetrieveUpdateDestroyAPIView):
    queryset = models.Customization.objects.all()
    serializer_class = CustomizationSerializer
    lookup_field = 'username'
    permission_classes = (permissions.IsAdminUser,)


class CustomizationList(ListCreateAPIView):
    queryset = models.Customization.objects.all()
    serializer_class = CustomizationSerializer
    permission_classes = (permissions.IsAdminUser,)
