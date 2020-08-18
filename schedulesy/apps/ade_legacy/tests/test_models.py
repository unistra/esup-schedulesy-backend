from django.test import TestCase

from schedulesy.apps.ade_api.models import LocalCustomization, Resource
from ..models import Customization


class CustomizationModelTestCase(TestCase):

    databases = '__all__'

    def tearDown(self):
        super().tearDown()
        Customization.objects.all().delete()

    def test_read_without_local_customization(self):
        Resource.objects.create(ext_id='10')
        customization = Customization.objects.create(
            id=1, resources='10', directory_id='42', username='user1')
        customization.configuration='{"mode":"dark"}'
        # The 'save' method automatically creates missing LocalCustomization
        # To simulate an oprhan line in Customization, we have to delete the LocalCustomization
        LocalCustomization.objects.get(customization_id=1).delete()
        lc = customization.local_customization
        self.assertIsInstance(lc, LocalCustomization)
        self.assertEqual(lc.resources.count(), 1)
        self.assertTrue(lc.resources.filter(ext_id='10').exists())

    def test_save_without_local_customization(self):
        Resource.objects.create(ext_id='10')
        Customization.objects.create(
            id=1, resources='10', directory_id='42', username='user1')
        local = LocalCustomization.objects.get(customization_id=1)

        self.assertEqual(local.resources.count(), 1)
        self.assertTrue(local.resources.filter(ext_id='10').exists())

    def test_save_empty_resources(self):
        Customization.objects.create(
            id=1, directory_id='42', username='user1')
        local = LocalCustomization.objects.get(customization_id=1)

        self.assertEqual(local.resources.count(), 0)

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

        self.assertEqual(local.resources.count(), 1)

    def test_save_adding_missing_resources_consistency(self):
        Resource.objects.create(ext_id='11')
        nb = Resource.objects.count()
        LocalCustomization.objects.create(customization_id=1)
        customization = Customization.objects.create(
            id=1, resources='11,12', directory_id='42', username='user1')
        self.assertEqual(Resource.objects.count(), nb)
        self.assertEqual(customization.resources, '11')

    def test_ics_calendar(self):
        Resource.objects.create(ext_id='11')
        Resource.objects.create(ext_id='12')
        customization = Customization.objects.create(
            id=1, resources='11,12', directory_id='42', username='user1')
        self.assertEqual("409a1639a5f7496086822b5f15e0e5bca85c161f.ics", customization.ics_calendar)

    def test_str(self):
        local = LocalCustomization.objects.create(customization_id=1, username='user1')
        self.assertEqual('user1', local.__str__())