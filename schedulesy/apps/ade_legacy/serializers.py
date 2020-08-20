import re

from django.urls import reverse
from rest_framework import serializers

from schedulesy.apps.ade_legacy.models import Customization


class CustomizationSerializer(serializers.ModelSerializer):

    configuration = serializers.SerializerMethodField()

    class Meta:
        model = Customization
        fields = '__all__'

    def to_internal_value(self, data):
        d = super().to_internal_value(data)
        if 'configuration' in data and type(data['configuration'] == dict):
            d['configuration'] = data['configuration']
        return d

    def get_configuration(self, obj):
        lc = obj.local_customization
        return lc.configuration if lc else {}
