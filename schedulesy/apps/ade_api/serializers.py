from django.conf import settings
from django.db.models.expressions import RawSQL
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied
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


class EventsSerializer(serializers.ModelSerializer):
    def to_representation(self, obj):
        def sanitize():
            if obj.fields['category'] != 'classroom':
                raise PermissionDenied('Only classrooms allowed')
            if fields['events']:
                fields['events']['instructors'] = {}
                for item in [x for x in fields['events']['events'] if 'instructors' in x]:
                    item.pop('instructors')

        fields = obj.fields or {}
        fields['events'] = obj.events
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user
            if not user.is_authenticated:
                sanitize()

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
        user = None
        data = {}
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user
        customization = Customization.objects.get(username=obj.username)
        if user.has_perm('ade_api.view_local_customization'):
            data = super().to_representation(obj)
            ade_serializer = AdeSerializer()
            resources_data = [
                {'id': r.ext_id, 'name': r.fields['name'],
                 'path': ' - '.join([g['name'] for g in r.fields['genealogy']])}
                for r in obj.resources.all()]
            data.update({'nb_events': obj.events_nb,
                         'ade': ade_serializer.to_representation(customization),
                         'resources': resources_data})
        else:
            # curl --request GET \
            #   --url https://my.path.com/api/info/example.json \
            #   --header 'Authorization: Token monpetittoken'
            data.update({'username': obj.username, 'resources': customization.resources})

        return data

    class Meta:
        model = LocalCustomization
        fields = ['id', 'customization_id', 'directory_id', 'username', 'configuration']
