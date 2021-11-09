import collections
import os

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from django.test import TestCase

from ..models import Access, AdeConfig, LocalCustomization, Resource

User = get_user_model()


class AdeConfigModelTestCase(TestCase):

    def test_save_singleton(self):
        AdeConfig.objects.create(
            ade_url='https://adewebcons-test.unistra.fr/',
            parameters={'projectId': '1'}
        )

        with self.assertRaises(IntegrityError):
            AdeConfig.objects.create(
                ade_url='https://adewebcons-test.unistra.fr/',
                parameters={'projectId': '2'}
            )


class LocalCustomizationGenerateEventsTestCase(TestCase):

    fixtures = ['tests/resources']

    def setUp(self):
        self.user_owner = User.objects.create_user('owner', password='pass')

    def test_with_empty_resources(self):
        lc = LocalCustomization.objects.create(
            customization_id='1', directory_id='42', username='owner')

        self.assertDictEqual(lc.events, {})

    def test_with_single_resource(self):
        res_bcd_media = Resource.objects.get(ext_id='1616')
        LocalCustomization.objects.create(
            customization_id='1', directory_id='42', username='owner')
        # Reload the events cached_property
        lc = LocalCustomization.objects.get(customization_id='1')
        lc.resources.add(res_bcd_media)

        self.assertEqual(len(lc.events['events']), 1)

    def test_with_multiple_resources(self):
        res_bcd_media = Resource.objects.get(ext_id='1616')
        instructor = Resource.objects.get(ext_id='23390')
        LocalCustomization.objects.create(
            customization_id='1', directory_id='42', username='owner')
        # Reload the events cached_property
        lc = LocalCustomization.objects.get(customization_id='1')
        lc.resources.add(res_bcd_media, instructor)
        data = lc.events

        self.assertEqual(len(data['events']), 2)
        self.assertEqual(len(data['classrooms']), 2)
        self.assertEqual(len(data['instructors']), 2)
        self.assertEqual(len(data['trainees']), 2)


class LocalCustomizationGenerateIcsCalendarTestCase(TestCase):

    fixtures = ['tests/resources']

    def setUp(self):
        self.user_owner = User.objects.create_user('owner', password='pass')

    def _assertIcsFields(self, filename, fields):
        with open(filename) as fh:
            d = collections.defaultdict(list)
            for k, v in map(lambda x: x.strip().split(':', 1), fh.readlines()):
                d[k].append(v)

            for k, v in fields.items():
                self.assertListEqual(
                    sorted(e.replace('\\', '') for e in d[k]),
                    sorted(v if isinstance(v, list) else [v]))

    def test_with_empty_resources(self):
        lc = LocalCustomization.objects.create(
            customization_id='1', directory_id='42', username='owner')
        lc.generate_ics_calendar()

        self.assertFalse(os.path.isfile(
            os.path.join(settings.MEDIA_ROOT, lc.ics_calendar_filename)))

    def test_with_single_resource(self):
        res_bcd_media = Resource.objects.get(ext_id='1616')
        LocalCustomization.objects.create(
            customization_id='1', directory_id='42', username='owner')
        # Reload the events cached_property
        lc = LocalCustomization.objects.get(customization_id='1')
        lc.resources.add(res_bcd_media)
        lc.generate_ics_calendar()

        # Testing formatted fields
        self._assertIcsFields(
            os.path.join(settings.MEDIA_ROOT, lc.ics_calendar_filename),
            {
                'LOCATION': 'BCD Media (COL  -SITE COLMAR, ESPE COLMAR BATIMENT PRINCIPAL)',
                'DESCRIPTION': 'Filières : M2 Biotechnologie HDnIntervenants : Gerard Toto',
                'GEO': '48.072084;7.352045'
            }
        )

    def test_with_multiple_resources(self):
        res_bcd_media = Resource.objects.get(ext_id='1616')
        instructor = Resource.objects.get(ext_id='23390')
        LocalCustomization.objects.create(
            customization_id='1', directory_id='42', username='owner')
        # Reload the events cached_property
        lc = LocalCustomization.objects.get(customization_id='1')
        lc.resources.add(res_bcd_media, instructor)
        lc.generate_ics_calendar()

        # Testing formatted fields
        self._assertIcsFields(
            os.path.join(settings.MEDIA_ROOT, lc.ics_calendar_filename),
            {
                'LOCATION': [
                    'BCD Media (COL  -SITE COLMAR, ESPE COLMAR BATIMENT PRINCIPAL)',
                    'A1.13 Informatique So (A1.16) (SCH  -SITE SCHILTIGHEIM, IUT LOUIS PASTEUR, TP)'
                ],
                'DESCRIPTION': [
                    'Filières : option NEInIntervenants : Yao Toto',
                    'Filières : M2 Biotechnologie HDnIntervenants : Gerard Toto'
                ],
                'GEO': [
                    '48.072084;7.352045'
                ]
            }
        )


class AccessTestCase(TestCase):

    def test_is_last_access(self):
        lc = LocalCustomization.objects.create(
            customization_id='1', directory_id='42', username='owner')
        self.assertTrue(lc.accesses.first().is_last_access)

        Access.objects.create(name='access', customization=lc)
        self.assertFalse(lc.accesses.first().is_last_access)

    def test_delete(self):
        lc = LocalCustomization.objects.create(
            customization_id='1', directory_id='42', username='owner')
        access = lc.accesses.first()
        access.delete()
        # Can not delete the last access of a customization
        self.assertTrue(Access.objects.filter(pk=access.pk).exists())

        Access.objects.create(name='access', customization=lc)
        access.delete()
        self.assertFalse(Access.objects.filter(pk=access.pk).exists())

class ResourceTestCase(TestCase):

    def test_lineage(self):
        r = Resource.objects.create(ext_id='1337')
        self.assertIn('1337', Resource.lineage(['1337']))
        r2 = Resource.objects.create(ext_id='666', parent=r)
        self.assertIn('666', Resource.lineage(['1337']))
        Resource.objects.create(ext_id='42', parent=r)
        Resource.objects.create(ext_id='314', parent=r2)
        Resource.objects.create(ext_id='3141', parent=r2)
        Resource.objects.create(ext_id='31415', parent=r2)
        self.assertIn('31415', Resource.lineage(['1337']))
        self.assertEqual(len(Resource.lineage(['1337'])), 6)
        s = Resource.objects.create(ext_id='314159')
        Resource.objects.create(ext_id='3141592', parent=s)
        self.assertEqual(len(Resource.lineage(['1337', '314159'])), 8)
        # Using set as argument
        self.assertEqual(len(Resource.lineage({'1337', '314159'})), 8)
        # Non existing resource
        self.assertEqual(len(Resource.lineage({'1337', '314159', '111'})), 8)
