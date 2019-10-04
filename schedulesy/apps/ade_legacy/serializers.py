from rest_framework import serializers

from schedulesy.apps.ade_api.models import LocalCustomization
from schedulesy.apps.ade_legacy.models import Customization


class CustomizationSerializer(serializers.ModelSerializer):
    def to_representation(self, obj):
        """
        builtins.dict representation of object. It will get configuration from LocalCustomization as well
        :param Customization obj: ADE customization
        :return: builtins.dict
        """
        data = super().to_representation(obj)
        try:
            lc = LocalCustomization.objects.get(customization_id=obj.id)
            data['configuration'] = lc.configuration
        except LocalCustomization.DoesNotExist as e:
            data['configuration'] = None
        return data

    def to_internal_value(self, data):
        d = super().to_internal_value(data)
        if 'configuration' in data and type(data['configuration'] == dict):
            d['configuration'] = data['configuration']
        return d

    class Meta:
        model = Customization
        fields = '__all__'
