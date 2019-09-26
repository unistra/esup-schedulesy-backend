from django.test import TestCase

from schedulesy.apps.ade_api.models import LocalCustomization, Resource
from ..models import Customization


class CustomizationModelTestCase(TestCase):

    def tearDown(self):
        super().tearDown()
        Customization.objects.all().delete()

    def test_save_without_local_customization(self):
        Customization.objects.create(
            id=1, resources='10', directory_id='42', username='user1')
        local = LocalCustomization.objects.get(customization_id=1)

        self.assertEqual(local.resources.count(), 1)
        self.assertTrue(local.resources.filter(ext_id='10').exists())

    def test_save_remove_unselected_resources(self):
        local = LocalCustomization.objects.create(customization_id=1)
        local.resources.add(Resource.objects.create(ext_id='11'),
                            Resource.objects.create(ext_id='12'))
        Customization.objects.create(
            id=1, resources='11', directory_id='42', username='user1')

        self.assertEqual(local.resources.count(), 1)
        self.assertFalse(local.resources.filter(ext_id='12').exists())

    def test_save_adding_missing_resources(self):
        local = LocalCustomization.objects.create(customization_id=1)
        local.resources.add(Resource.objects.create(ext_id='11'))
        Customization.objects.create(
            id=1, resources='11,12', directory_id='42', username='user1')

        self.assertEqual(local.resources.count(), 2)
