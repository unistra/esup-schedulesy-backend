from rest_framework import serializers
from rest_framework.reverse import reverse

from schedulesy.apps.ade_api.models import LocalCustomization
from schedulesy.apps.ade_api.utils import force_https
from .models import Access, AdeConfig, LocalCustomization, Resource


class ResourceSerializer(serializers.ModelSerializer):
    def to_representation(self, obj):
        if 'children' in obj.fields:
            for child in obj.fields['children']:
                child['id'] = force_https(reverse(
                    'api:resource',
                    kwargs={
                        'ext_id': child['id'],
                        'format': self.context['format']
                    },
                    request=self.context['request']))
            new_list = sorted(
                obj.fields['children'], key=lambda k: k['name'].lower())
            obj.fields['children'] = new_list
        return obj.fields

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


class LocalCustomizationSerializer(serializers.ModelSerializer):
    def to_representation(self, obj):
        """
        Merges all events
        :param LocalCustomization obj:
        :return:
        """
        resources = obj.resources.all()
        if len(resources) == 0:
            return None
        if len(resources) == 1:
            return resources[0].events
        result = {}
        events = {l['id']: l for l in
               [item for sublist in [x.events['events'] for x in resources if 'events' in x.events] for item
                in sublist]}
        result['events'] = events.values()
        for resource_type in ('trainees', 'instructors', 'classrooms'):
            result[resource_type] = {k: v for d in [x.events[resource_type] for x in resources if resource_type in x.events] for k, v in d.items()}
        return result

    class Meta:
        model = LocalCustomization
