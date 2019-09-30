from django.test import TestCase

from .utils import ADEMixin
from ..models import Fingerprint, Resource
from ..refresh import Refresh


class RefreshCategoryTestCase(ADEMixin, TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.category = 'classroom'
        cls.method = Refresh.METHOD_GET_RESOURCE
        cls.data_key = f'{Refresh.METHOD_GET_RESOURCE}-{cls.category}'

    def test_initial_classroom_refresh(self):
        refresh = Refresh()
        refresh.refresh_category(self.category)

        self.assertEqual(Resource.objects.count(), 19)
        self.assertEqual(refresh.data[self.data_key]['created'], 19)
        self.assertTrue(Fingerprint.objects
                        .filter(ext_id=self.category, method=self.method)
                        .exists())

        # Testing genealogy
        fields = {'fields__category': self.category}
        res_colmar = Resource.objects.get(ext_id=30622, **fields)
        res_espe_colmar = Resource.objects.get(ext_id=30628, **fields)
        res_bcd_media = Resource.objects.get(ext_id=1616, **fields)

        self.assertEqual(res_bcd_media.parent, res_espe_colmar)
        self.assertEqual(res_espe_colmar.parent, res_colmar)

    def test_classroom_refresh_with_existing_elements(self):
        fp = Fingerprint.objects.create(
            ext_id=self.category, method='getResources',
            fingerprint='unittest')
        res_bcd_media = Resource.objects.create(
            ext_id=1616, fields={'category': self.category})

        refresh = Refresh()
        refresh.refresh_category(self.category)

        self.assertEqual(Resource.objects.count(), 19)
        self.assertEqual(refresh.data[self.data_key]['created'], 18)
        self.assertEqual(refresh.data[self.data_key]['updated'], 1)
        self.assertNotEqual(
            (
                Fingerprint.objects
                .get(ext_id=self.category, method=self.method).fingerprint
            ),
            'unittest')

        # Testing genealogy
        fields = {'fields__category': self.category}
        res_espe_colmar = Resource.objects.get(ext_id=30628, **fields)
        res_bcd_media = Resource.objects.get(ext_id=1616, **fields)

        self.assertEqual(res_bcd_media.parent, res_espe_colmar)


class RefreshResourceTestCase(ADEMixin, TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.category = 'classroom'
        cls.method = Refresh.METHOD_GET_RESOURCE
        cls.data_key = f'{Refresh.METHOD_GET_RESOURCE}-{cls.category}'
