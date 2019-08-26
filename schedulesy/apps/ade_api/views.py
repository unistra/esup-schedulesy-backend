import json

from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, JsonResponse
from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response
from rest_framework.status import HTTP_404_NOT_FOUND

from schedulesy.apps.ade_api.refresh import Refresh
from schedulesy.apps.ade_api.serializers import ResourceSerializer
from schedulesy.apps.ade_api.models import Resource


def refresh(request):
    if request.method == "GET":
        data = Refresh().data
        return JsonResponse(data)


class ResourceDetail(RetrieveAPIView):
    queryset = Resource.objects.all()
    serializer_class = ResourceSerializer

    def get(self, request, *args, **kwargs):
        try :
            obj = self.queryset.get(ext_id=self.kwargs['ext_id'])
        except ObjectDoesNotExist:
            return Response(status=HTTP_404_NOT_FOUND, data={'error':'not found'})

        print("{} ({}) : {}".format(self.kwargs['ext_id'], type(self.kwargs['ext_id']), obj))
        serializer = ResourceSerializer(obj, context={'request': request})
        return Response(serializer.data)
