from django.http import HttpRequest
from django.test import TestCase

from ..models import Customization
from ..serializers import CustomizationSerializer

# class CustomizationSerializerTestCase(TestCase):

# databases = '__all__'

#     def setUp(self):
#         request = HttpRequest()
#         request.META = {
#             'SERVER_NAME': 'testserver.com',
#             'SERVER_PORT': 80
#         }
#         self.context = {'request': request}

#     def tearDown(self):
#         Customization.objects.all().delete()

#     def test_get_ics_calendar(self):
#         obj = Customization.objects.create(
#             id=1, directory_id='1', username='owner')
#         serializer = CustomizationSerializer(data=obj, context=self.context)
#         self.assertEqual(serializer.get_ics_calendar(obj),
#                          'http://testserver.com/api/calendar/owner/export')

#     def test_get_ics_calendar_without_local_customization(self):
#         # Use the bulk create to prevent the call of the save method
#         Customization.objects.bulk_create([
#             Customization(id=1, directory_id='1', username='owner')
#         ])
#         obj = Customization.objects.get(id=1)
#         serializer = CustomizationSerializer(data=obj, context=self.context)
#         # Local customization is created on call if doesn't exist
#         self.assertEqual(serializer.get_ics_calendar(obj), 'http://testserver.com/api/calendar/owner/export')
