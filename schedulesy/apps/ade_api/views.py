from django.http import JsonResponse
from rest_framework import generics, permissions
from rest_framework.response import Response

from .models import DisplayType, Resource
from .refresh import Refresh
from .serializers import ResourceSerializer


def refresh(request):
    if request.method == "GET":
        data = Refresh().data
        return JsonResponse(data)


class ResourceDetail(generics.RetrieveAPIView):
    queryset = Resource.objects.all()
    serializer_class = ResourceSerializer
    permission_classes = (permissions.AllowAny, )
    lookup_field = 'ext_id'


class DisplayTypeList(generics.ListAPIView):
    queryset = DisplayType.objects.all()
    permission_classes = (permissions.AllowAny, )

    def list(self, request, *args, **kwargs):
        return Response(self.get_queryset().values_list('name', flat=True))
