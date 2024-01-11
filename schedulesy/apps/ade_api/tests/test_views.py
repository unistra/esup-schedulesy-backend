import base64
import datetime
import json

from django.contrib.auth import get_user_model
from django.http import HttpRequest
from django.test import TestCase
from django.urls import reverse
from rest_framework_simplejwt.tokens import AccessToken

from schedulesy.apps.ade_api.utils import generate_color_from_name

from ...ade_legacy.models import Customization
from ...ade_legacy.tests.test_views import authenticated_client
from ..models import Access, AdeConfig, LocalCustomization, Resource
from ..views import AccessDeletePermission

User = get_user_model()


class AuthCase(TestCase):
    fixtures = ['tests/users.json']

    @classmethod
    def setUpTestData(cls):
        cls.no_auth = User.objects.get(pk=5)
        cls.non_authorized_access = AccessToken().for_user(cls.no_auth)
        cls.expired = (
            AccessToken()
            .for_user(cls.no_auth)
            .set_exp(datetime.datetime.now() - datetime.timedelta(days=365))
        )


class AdminTestCase(AuthCase):
    def test_sync_customization_no_auth(self):
        self.client.login(username='no_auth', password='password')
        response = self.client.get(reverse('api:sync_customization'))
        self.assertEqual(302, response.status_code)

    def test_sync_customization_super_user(self):
        Customization.objects.create(
            id=1, resources='10', directory_id='42', username='user1'
        )
        LocalCustomization.objects.get(customization_id=1).delete()
        c2 = Customization.objects.create(
            id=2, resources='10', directory_id='666', username='user2'
        )
        c2.delete()
        Customization.objects.create(
            id=3, resources='10', directory_id='111', username='user3'
        )
        self.client.login(username='super_user', password='password')
        response = self.client.get(reverse('api:sync_customization'))
        self.assertEqual(200, response.status_code)
        self.assertIsNotNone(Customization.objects.get(username='user1'))
        self.assertIsNotNone(LocalCustomization.objects.get(username='user1'))
        self.assertIsNotNone(Customization.objects.get(username='user3'))
        self.assertIsNotNone(LocalCustomization.objects.get(username='user3'))
        with self.assertRaises(Customization.DoesNotExist):
            self.assertIsNotNone(Customization.objects.get(username='user2'))
        with self.assertRaises(LocalCustomization.DoesNotExist):
            self.assertIsNotNone(LocalCustomization.objects.get(username='user2'))


class AccessListTestCase(AuthCase):
    def setUp(self):
        super().setUp()
        self.view_url = '/api/customization/{username}/uuid.json'

    def test_create_access(self):
        User.objects.create_user('owner', password='pass')
        LocalCustomization.objects.create(
            customization_id='1', directory_id='42', username='owner'
        )

        self.client.login(username='owner', password='pass')
        response = self.client.post(
            self.view_url.format(username='owner'), {'name': 'testing'}
        )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(Access.objects.filter(customization__username='owner').exists())

    def test_list_access(self):
        User.objects.create_user('owner', password='pass')
        User.objects.create_user('not-owner', password='pass')
        lc_owner = LocalCustomization.objects.create(
            customization_id='1', directory_id='42', username='owner'
        )
        Access.objects.create(customization=lc_owner, name='access1')

        self.client.login(username='owner', password='pass')
        response = self.client.get(self.view_url.format(username='owner'))
        data = json.loads(response.content.decode('utf-8'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 2)
        self.assertIn('access1', [d['name'] for d in data])
        # Defaut access created with LocalCustomization
        self.assertIn('owner', [d['name'] for d in data])


class AccessDeletePermissionTestCase(TestCase):
    def test_authorize_access_deletion(self):
        request = HttpRequest()
        lc = LocalCustomization.objects.create(
            customization_id='1', directory_id='42', username='owner'
        )
        access = Access.objects.create(customization=lc, name='access1')

        self.assertTrue(
            AccessDeletePermission().has_object_permission(request, None, access)
        )

    def test_prevent_last_access_deletion(self):
        request = HttpRequest()
        lc = LocalCustomization.objects.create(
            customization_id='1', directory_id='42', username='owner'
        )
        access = lc.accesses.first()

        self.assertFalse(
            AccessDeletePermission().has_object_permission(request, None, access)
        )


class AccessDeleteTestCase(TestCase):
    def test_delete_access(self):
        view_url = '/api/customization/{username}/uuid/{key}.json'
        User.objects.create_user('owner', password='pass')
        lc = LocalCustomization.objects.create(
            customization_id='1', directory_id='42', username='owner'
        )
        access = Access.objects.create(customization=lc, name='access1')

        self.client.login(username='owner', password='pass')
        response = self.client.delete(view_url.format(username='owner', key=access.key))

        self.assertEqual(response.status_code, 204)
        self.assertFalse(Access.objects.filter(name='access1').exists())


class AdeConfigDetailTestCase(AuthCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.view_url = '/api/ade_config.json'
        AdeConfig.objects.create(
            ade_url='https://adewebcons-test.unistra.fr/', parameters={'projectId': '1'}
        )

    def test_view_auth(self):
        response = self.client.get(
            self.view_url,
            HTTP_AUTHORIZATION='Bearer ' + str(self.non_authorized_access),
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))

        self.assertDictEqual(
            data,
            {
                'base_url': 'https://adewebcons-test.unistra.fr/',
                'params': {'projectId': '1'},
            },
        )

    def test_view_no_auth(self):
        response = self.client.get(self.view_url)
        self.assertEqual(response.status_code, 403)


class ResourceDetailTestCase(AuthCase):
    def test_resource_with_empty_fields_auth(self):
        view_url = '/api/resource/{ext_id}.json'
        Resource.objects.create(ext_id=30622)

        response = self.client.get(
            view_url.format(ext_id=30622),
            HTTP_AUTHORIZATION=f'Bearer {self.non_authorized_access}',
        )
        data = json.loads(response.content.decode('utf-8'))

        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(data, {})

    def test_resource_with_empty_fields_no_auth(self):
        view_url = '/api/resource/{ext_id}.json'
        Resource.objects.create(ext_id=30622)
        response = self.client.get(view_url.format(ext_id=30622))
        self.assertEqual(response.status_code, 403)

    def test_resource_with_fields(self):
        view_url = '/api/resource/{ext_id}.json'
        Resource.objects.create(
            ext_id=30622,
            fields={
                'children': [
                    {
                        'id': '30628',
                        'name': 'ESPE COLMAR BATIMENT PRINCIPAL',
                        'has_children': True,
                    },
                    {
                        'id': '30623',
                        'name': 'ESPE COLMAR AILE JOFFRE',
                        'has_children': True,
                    },
                    {
                        'id': '30715',
                        'name': 'Gymnases IUFM COLMAR',
                        'has_children': True,
                    },
                ]
            },
        )

        response = self.client.get(
            view_url.format(ext_id=30622),
            HTTP_AUTHORIZATION='Bearer ' + str(self.non_authorized_access),
        )
        data = json.loads(response.content.decode('utf-8'))

        self.assertEqual(response.status_code, 200)
        self.assertListEqual(
            data['children'],
            [
                {
                    'has_children': True,
                    'id': 'https://testserver/api/resource/30623.json/',
                    'name': 'ESPE COLMAR AILE JOFFRE',
                    'selectable': False,
                },
                {
                    'has_children': True,
                    'id': 'https://testserver/api/resource/30628.json/',
                    'name': 'ESPE COLMAR BATIMENT PRINCIPAL',
                    'selectable': False,
                },
                {
                    'has_children': True,
                    'id': 'https://testserver/api/resource/30715.json/',
                    'name': 'Gymnases IUFM COLMAR',
                    'selectable': False,
                },
            ],
        )


class CalendarExportTestCase(TestCase):
    fixtures = ['tests/resources']

    def test_calendar_export(self):
        view_url = '/api/calendar/{uuid}/export'
        lc = LocalCustomization.objects.create(
            customization_id='1', directory_id='42', username='owner'
        )
        access = lc.accesses.first()
        # Reload the events cached_property
        lc = LocalCustomization.objects.get(customization_id='1')
        lc.resources.add(Resource.objects.get(ext_id='1616'))
        lc.generate_ics_calendar()

        response = self.client.get(view_url.format(uuid=access.key))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/calendar')


class InfoCase(TestCase):
    fixtures = ['tests/users.json', 'tests/resources']

    @classmethod
    def setUpTestData(cls):
        cls.no_auth = User.objects.get(pk=5)
        Customization.objects.create(
            username='no_auth', directory_id='42', resources='1616'
        )
        cls.view_url = reverse(
            'api:info', kwargs={'username': 'no_auth', 'format': 'json'}
        )
        cls.admin = User.objects.get(pk=1)
        cls.staff = User.objects.get(pk=6)

    def test_info_no_auth(self):
        response = self.client.get(self.view_url)
        self.assertEqual(response.status_code, 403)

    def test_info_no_perm(self):
        self.client.login(username='no_auth', password='password')
        response = self.client.get(self.view_url)
        self.assertEqual(response.status_code, 403)

    def check_data(self, response):
        data = json.loads(response.content.decode('utf-8'))
        keys = [
            'id',
            'customization_id',
            'directory_id',
            'username',
            'configuration',
            'nb_events',
            'ade',
            'resources',
        ]
        self.assertTrue(all(k in data for k in keys))
        self.assertEqual(data['directory_id'], '42')
        self.assertEqual(data['username'], 'no_auth')

    def test_info_admin(self):
        self.client.login(username='super_user', password='password')
        response = self.client.get(self.view_url)
        self.assertEqual(response.status_code, 200)
        self.check_data(response)

    def test_token_admin(self):
        response = authenticated_client(self.admin).get(self.view_url)
        self.assertEqual(response.status_code, 200)
        self.check_data(response)

    def test_token_staff(self):
        response = authenticated_client(self.staff).get(self.view_url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        keys = ['username', 'resources']
        self.assertTrue(all(k in data for k in keys))
        self.assertEqual(data['resources'], '1616')


class EventDetailTestCase(AuthCase):
    fixtures = ['tests/users.json', 'tests/resources']

    def _call_events(self, ext_id, reverse_name='api:events', **kwargs):
        url = reverse(reverse_name, kwargs={'ext_id': ext_id, 'format': 'json'})
        response = self.client.get(url, **kwargs)
        return response

    def _is_intructor(self, response):
        data = json.loads(response.content.decode('utf-8'))
        return (
            'instructors' in data['events']
            and 'instructors' in data['events']['events'][0]
        )

    def test_events_no_auth(self):
        response = self._call_events(
            1616, HTTP_AUTHORIZATION=f'Bearer {self.non_authorized_access}'
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self._is_intructor(response))

    def test_events_public_classroom_expired(self):
        response = self._call_events(1616, HTTP_AUTHORIZATION=f'Bearer {self.expired}')
        self.assertEqual(response.status_code, 403)

    def test_events_public_classroom(self):
        response = self._call_events(1616)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(self._is_intructor(response))

    def test_events_public_instructor(self):
        response = self._call_events(23390)
        self.assertEqual(response.status_code, 403)

    def test_events_list_public_classroom_ok(self):
        r = Resource.objects.create(ext_id=7542)
        r.events = {
            "events": [
                {
                    "id": "222486",
                    "date": "20/11/2023",
                    "name": "Management du personnel",
                    "note": "",
                    "color": "#ffffff",
                    "endHour": "13:00",
                    "duration": "12",
                    "trainees": ["17350"],
                    "startHour": "10:00",
                    "activityId": "46328",
                    "classrooms": ["7542"],
                    "lastUpdate": "10/23/2023 10:22",
                    "instructors": ["27259"],
                }
            ],
            "trainees": {"17350": {"name": "Cours 1 PGC"}},
            "classrooms": {
                "7542": {
                    "name": "107",
                    "genealogy": ["HOP  -CAMPUS HOPITAL CIVIL", "CARDO"],
                    "geolocation": [],
                }
            },
            "instructors": {"27259": {"name": "Serge Serge"}},
        }
        r.fields = {
            "id": "7542",
            "fax": "",
            "tag": "leaf",
            "url": "",
            "city": "",
            "code": "1770411",
            "info": "",
            "name": "107",
            "path": "HOP  -CAMPUS HOPITAL CIVIL.CARDO.",
            "size": "36",
            "type": "SEN-Salle d'enseignement",
            "codeX": "HCI -HOPITAL CIVIL",
            "codeY": "LE CARDO",
            "codeZ": "Abyla/Validee/Web",
            "color": "255,255,255",
            "email": "",
            "state": "",
            "number": "1",
            "parent": "7429",
            "country": "LE CARDO",
            "isGroup": "false",
            "lastDay": "4",
            "manager": "",
            "zipCode": "",
            "address1": "",
            "address2": "7542",
            "category": "classroom",
            "consumer": "false",
            "creation": "04/09/2019 08:03",
            "fatherId": "7429",
            "firstDay": "0",
            "lastSlot": "16",
            "lastWeek": "45",
            "timezone": "107",
            "firstSlot": "0",
            "firstWeek": "3",
            "genealogy": [
                {"id": "classroom", "code": "", "name": "classroom"},
                {"id": "315", "code": "", "name": "HOP  -CAMPUS HOPITAL CIVIL"},
                {"id": "7429", "code": "", "name": "CARDO"},
            ],
            "telephone": "17",
            "fatherName": "CARDO",
            "lastUpdate": "12/18/2023 15:38",
            "jobCategory": "CARDO",
            "nbEventsPlaced": "455",
            "availableQuantity": "-1",
            "durationInMinutes": "60120",
        }
        r.save()
        response = self._call_events(
            base64.urlsafe_b64encode(b'[1616,7542]').decode(), 'api:events_list'
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(self._is_intructor(response))
        data = json.loads(response.content.decode('utf-8'))
        ids = [event['id'] for event in data['events']['events']]
        self.assertIn('191050', ids)
        self.assertIn('222486', ids)
        colors = [event['color'] for event in data['events']['events']]
        self.assertIn(generate_color_from_name('7542'), colors)

    def test_events_list_public_classroom_unknown_resource(self):
        response = self._call_events(
            base64.urlsafe_b64encode(b'[1234]').decode(), 'api:events_list'
        )
        self.assertEqual(response.status_code, 404)

    def test_events_list_public_classroom_wrong_encoding(self):
        response = self._call_events('abcd', 'api:events_list')
        self.assertEqual(response.status_code, 404)


class UtilsTestCase(TestCase):
    def test_generate_color_from_name(self):
        self.assertEqual(generate_color_from_name('test'), '#45a113')
