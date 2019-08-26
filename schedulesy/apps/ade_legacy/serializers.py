from rest_framework import serializers

from schedulesy.apps.ade_legacy.models import Customization


class WEdtpersoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customization
        fields = '__all__'
