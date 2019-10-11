import re

from django.urls import reverse
from rest_framework import serializers

from schedulesy.apps.ade_legacy.models import Customization


class CustomizationSerializer(serializers.ModelSerializer):

    configuration = serializers.SerializerMethodField()
    ics_calendar = serializers.SerializerMethodField()

    class Meta:
        model = Customization
        fields = '__all__'

    # @staticmethod
    # def validate_resources(value):
    #     if value == "":
    #         return value
    #     if re.search("^([0-9]+)(,[0-9]+)*$", value) is None:
    #         raise serializers.ValidationError("Invalid resources format")
    #     return value

    def get_configuration(self, obj):
        lc = obj.local_customization
        return lc.configuration if lc else {}

    def get_ics_calendar(self, obj):
        lc = obj.local_customization
        if lc:
            request = self.context['request']
            return '{scheme}://{domain}{filename}'.format(
                scheme=request.is_secure() and 'https' or 'http',
                domain=request.get_host(),
                filename=reverse(
                    'api:calendar-export', kwargs={'username': lc.username})
            )
        return ''
