from rest_framework import serializers
from rest_framework.reverse import reverse

from .models import Access, AdeConfig, LocalCustomization, Resource
from .utils import force_https


class ResourceSerializer(serializers.ModelSerializer):
    def to_representation(self, obj):
        fields = obj.fields or {}
        if 'children' in fields:
            for child in fields['children']:
                child['id'] = force_https(reverse(
                    'api:resource',
                    kwargs={
                        'ext_id': child['id'],
                        'format': self.context['format']
                    },
                    request=self.context['request']))
            new_list = sorted(
                fields['children'], key=lambda k: k['name'].lower())
            fields['children'] = new_list
        return fields

    class Meta:
        model = Resource


class AdeConfigSerializer(serializers.ModelSerializer):
    def to_representation(self, obj):
        return {
            'base_url': obj.ade_url,
            'params': obj.parameters
        }

    class Meta:
        model = AdeConfig


class AccessSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        validated_data['customization'] = self.context.get('customization')
        return super().create(validated_data)

    class Meta:
        model = Access
        exclude = ('id',)
        extra_kwargs = {
            'customization': {
                'write_only': True, 'required': False, 'default': ''
            }
        }


class CalendarSerializer(serializers.ModelSerializer):

    class Meta:
        model = LocalCustomization
        fields = ('events',)
