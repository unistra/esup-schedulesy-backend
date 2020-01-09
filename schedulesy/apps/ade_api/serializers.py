from django.conf import settings
from django.db.models.expressions import RawSQL
from rest_framework import serializers
from rest_framework.reverse import reverse

from .models import Access, AdeConfig, LocalCustomization, Resource
from .utils import force_https
from ..ade_legacy.models import Customization


class ResourceSerializer(serializers.ModelSerializer):

    def to_representation(self, obj):
        fields = obj.fields or {}
        if 'children' in fields:
            # Get number of events per child
            children_nb_events = dict(
                obj.children
                    .annotate(nb_events=RawSQL(
                    "jsonb_array_length(events->'events')", ()))
                    .values_list('ext_id', 'nb_events'))

            for child in fields['children']:
                child_id = child['id']
                child['id'] = force_https(reverse(
                    'api:resource',
                    kwargs={
                        'ext_id': child_id,
                        'format': self.context['format']
                    },
                    request=self.context['request']))
                nb_events = children_nb_events.get(child_id)
                child['selectable'] = bool(
                    obj.parent is not None
                    and nb_events
                    and not nb_events > settings.ADE_MAX_EVENTS)
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


class AdeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customization
        fields = '__all__'


class InfoSerializer(serializers.ModelSerializer):

    def to_representation(self, obj):
        data = super().to_representation(obj)
        customization = Customization.objects.get(username=obj.username)
        ade_serializer = AdeSerializer()
        data.update({'ade': ade_serializer.to_representation(customization)})
        return data

    class Meta:
        model = LocalCustomization
        depth = 1
        fields = '__all__'
