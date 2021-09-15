from django.test import TestCase
import responses

from .utils import ADEMixin, InfocentreMixin
from ..models import Fingerprint, Resource, LocalCustomization
from ..refresh import Refresh
from ...ade_legacy.models import Customization


class RefreshCategoryTestCase(ADEMixin, TestCase):

    def setUp(self):
        super().setUp()
        self.refresh = Refresh()
        self.category = 'classroom'
        self.method = Refresh.METHOD_GET_RESOURCE
        self.data_key = f'{Refresh.METHOD_GET_RESOURCE}-{self.category}'
        self.add_getresources_response(self.category)

    def test_initial_classroom_refresh(self):
        self.refresh.refresh_category(self.category)

        self.assertEqual(Resource.objects.count(), 20)
        self.assertEqual(self.refresh.data[self.data_key]['created'], 20)
        self.assertTrue(Fingerprint.objects
                        .filter(ext_id=self.category, method=self.method)
                        .exists())

        # Testing genealogy
        fields = {'fields__category': self.category}
        res_colmar = Resource.objects.get(ext_id=30622, **fields)
        res_espe_colmar = Resource.objects.get(ext_id=30628, **fields)
        res_espe_additional = Resource.objects.get(ext_id=1111, **fields)
        res_bcd_media = Resource.objects.get(ext_id=1616, **fields)

        self.assertEqual(res_bcd_media.parent, res_espe_additional)
        self.assertEqual(res_espe_additional.parent, res_espe_colmar)
        self.assertEqual(res_espe_colmar.parent, res_colmar)

    def test_classroom_refresh_with_existing_elements(self):
        fp = Fingerprint.objects.create(
            ext_id=self.category, method='getResources',
            fingerprint='unittest')
        Resource.objects.create(
            ext_id=1359, fields={'category': 'wrong', 'name': 'wrong'})
        Resource.objects.create(
            ext_id=1111, fields={'category': 'classroom', 'name': 'wrong'})

        self.refresh.refresh_category(self.category)

        self.assertEqual(Resource.objects.count(), 20)
        self.assertEqual(self.refresh.data[self.data_key]['created'], 19)
        self.assertEqual(self.refresh.data[self.data_key]['updated'], 1)
        self.assertEqual(self.refresh.data[self.data_key]['deleted'], 1)
        self.assertNotEqual(
            (
                Fingerprint.objects
                .get(ext_id=self.category, method=self.method).fingerprint
            ),
            'unittest')

        # Testing genealogy
        fields = {'fields__category': self.category}
        res_espe_additional = Resource.objects.get(ext_id=1111, **fields)
        res_bcd_media = Resource.objects.get(ext_id=1616, **fields)

        self.assertEqual(res_bcd_media.parent, res_espe_additional)

    def test_classroom_refresh_customization_cascade(self):
        Fingerprint.objects.create(
            ext_id=self.category, method='getResources',
            fingerprint='unittest')
        r_1616 = Resource.objects.create(
            ext_id=1616, fields={'category': self.category})
        # inconsistency due to id recycling (verified category is classroom but this id
        # already exists with category 'wrong'
        r_1359 = Resource.objects.create(
            ext_id=1359, fields={'category': 'wrong', 'name': 'wrong'})
        # local has 2 resources : 1616 and 1359
        local = LocalCustomization.objects.create(customization_id=1)
        local.resources.add(r_1359, r_1616)
        Customization.objects.create(
            id=1, resources='1616,1359', directory_id='42', username='user1')
        # lc2 has 1 resource : 1359
        lc2 = LocalCustomization.objects.create(customization_id=2, username='cascade')
        lc2.resources.add(r_1359, r_1616)
        Customization.objects.create(
            id=2, resources='1359', directory_id='69', username='cascade')

        # Main action
        self.refresh.refresh_category(self.category)

        # Tests
        self.assertEqual(Resource.objects.count(), 20)
        self.assertEqual(self.refresh.data[self.data_key]['created'], 19)
        self.assertEqual(self.refresh.data[self.data_key]['updated'], 1)
        self.assertEqual(self.refresh.data[self.data_key]['deleted'], 1)

        # New count of linked resources
        self.assertEqual(local.resources.count(), 1)
        self.assertFalse(local.resources.filter(ext_id='1359').exists())
        self.assertTrue(local.resources.filter(ext_id='1616').exists())
        # Cascade in customization table
        ade1 = Customization.objects.get(id=1)
        self.assertEqual(ade1.resources, '1616')
        ade2 = Customization.objects.get(id=2)
        self.assertEqual(ade2.resources, '')


class RefreshResourceTestCase(ADEMixin, InfocentreMixin, TestCase):

    def setUp(self):
        super().setUp()
        self.refresh = Refresh()

    def test_refresh_existing_resource(self):
        self.add_getresources_response()
        self.add_getevents_response(1616)

        self.refresh.refresh_single_resource(1616, 'op')

        # Update the resource
        res_bcd_media = Resource.objects.get(ext_id=1616)
        res_bcd_media.parent = Resource.objects.get(ext_id="30618")
        res_bcd_media.fields['name'] = 'Renamed resource'
        res_bcd_media.save()

        self.refresh.refresh_single_resource(1616, 'op')
        res_bcd_media = Resource.objects.get(ext_id=1616)

        self.assertEqual(res_bcd_media.fields['name'], 'BCD Media')
        self.assertEqual(res_bcd_media.parent.ext_id, '1111')

    def test_refresh_resource_single_event(self):
        self.add_getresources_response()
        self.add_getevents_response(1616)

        self.refresh.refresh_single_resource(1616, 'op')
        res_bcd_media = Resource.objects.get(ext_id=1616)
        events = res_bcd_media.events

        self.assertDictEqual(
            events['trainees'], {'32291': {'name': 'M2 Biotechnologie HD'}})
        self.assertIn('1616', events['classrooms'])
        self.assertListEqual(
            events['classrooms']['1616']['genealogy'],
            ['COL  -SITE COLMAR', 'ESPE COLMAR BATIMENT PRINCIPAL', 'ADDITIONAL BRANCH'])
        self.assertDictEqual(
            events['instructors'], {'23390': {'name': 'Gerard Toto'}})
        self.assertEqual(events['classrooms']['1616']['geolocation'], [48.607508, 7.708025, 0.0])

    def test_refresh_resource_multiple_events(self):
        self.add_getresources_response()
        self.add_getevents_response(23390)

        self.refresh.refresh_single_resource(23390, 'op')
        instructor = Resource.objects.get(ext_id=23390)
        events = instructor.events

        self.assertDictEqual(
            events['trainees'], {
                '32291': {'name': 'M2 Biotechnologie HD'},
                '23613': {'name': 'option NEI'}
            })
        self.assertIn('2491', events['classrooms'])
        self.assertListEqual(
            events['classrooms']['2491']['genealogy'],
            ['SCH  -SITE SCHILTIGHEIM', 'IUT LOUIS PASTEUR', 'TP'])
        self.assertDictEqual(
            events['instructors'], {
                '23390': {'name': 'Gerard Toto'},
                '26840': {'name': 'Yao Toto'}
            })


class RefreshEventTestCase(ADEMixin, InfocentreMixin, TestCase):

    def setUp(self):
        super().setUp()
        self.refresh = Refresh()

    def test_add_missing_events(self):
        self.add_getresources_response()
        self.add_getevents_response(1616)

        self.refresh.refresh_all()
        self.refresh.refresh_event(191050, 1, [1616], 'op')

        self.assertTrue(Resource.objects.get(ext_id=1616).events)
        self.assertEqual(
            Resource.objects.filter(events__isnull=False).count(), 1)

    def test_remove_old_events(self):
        self.add_getresources_response()
        self.add_getevents_response(1616)
        self.add_getevents_response(23390)

        self.refresh.refresh_all()
        # Add the event 191050 on some random resource
        Resource.objects.filter(ext_id=1616).update(
            events={'events': [{'id': 187912}]}
        )
        self.refresh.refresh_event(191050, 1, [1616], 'op')

        self.assertEqual(
            Resource.objects.filter(events__isnull=False).count(), 1)
        self.assertFalse(
            Resource.objects
            .filter(ext_id=1616, events__events__contains=[{'id': '187912'}])
            .exists()
        )
