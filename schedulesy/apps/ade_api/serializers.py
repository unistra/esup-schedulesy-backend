from rest_framework import serializers
from rest_framework.reverse import reverse

from schedulesy.models import Resource


class ResourceSerializer(serializers.ModelSerializer):
    def to_representation(self, obj):
        for child in obj.fields['children']:
            child['id'] = reverse('api:resource',
                                  kwargs={'ext_id': child['id']},
                                  request=self.context['request'])
        return obj.fields

    class Meta:
        model = Resource
