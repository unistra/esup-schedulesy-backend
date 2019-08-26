from rest_framework import serializers

from schedulesy.apps.ade_legacy.models import Edtperso


class WEdtpersoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Edtperso
        fields = '__all__'
