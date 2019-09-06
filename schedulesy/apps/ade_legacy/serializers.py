from rest_framework import serializers

from schedulesy.apps.ade_legacy.models import Customization


class CustomizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customization
        fields = '__all__'
