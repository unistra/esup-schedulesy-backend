import json

from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Access, AdeConfig, LocalCustomization, Resource


User = get_user_model()


class AccessListTestCase(TestCase):

    def setUp(self):
        super().setUp()
        self.view_url = '/api/customization/{username}/uuid.json'

    def test_create_access(self):
        User.objects.create_user('owner', password='pass')
        LocalCustomization.objects.create(
            customization_id='1', directory_id='42', username='owner')

        self.client.login(username='owner', password='pass')
        response = self.client.post(
            self.view_url.format(username='owner'),
            {'name': 'testing'}
        )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(
            Access.objects.filter(customization__username='owner').exists())

    def test_list_access(self):
        User.objects.create_user('owner', password='pass')
        User.objects.create_user('not-owner', password='pass')
        lc_owner = LocalCustomization.objects.create(
            customization_id='1', directory_id='42', username='owner')
        lc_not_owner = LocalCustomization.objects.create(
            customization_id='2', directory_id='43', username='not-owner')
        Access.objects.create(customization=lc_owner, name='access1')
        Access.objects.create(customization=lc_not_owner, name='access2')

        self.client.login(username='owner', password='pass')
        response = self.client.get(self.view_url.format(username='owner'))
        data = json.loads(response.content.decode('utf-8'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name'], 'access1')


class AccessDeleteTestCase(TestCase):

    def test_delete_access(self):
        view_url = '/api/customization/{username}/uuid/{key}.json'
        User.objects.create_user('owner', password='pass')
        lc = LocalCustomization.objects.create(
            customization_id='1', directory_id='42', username='owner')
        access = Access.objects.create(customization=lc, name='access1')

        self.client.login(username='owner', password='pass')
        response = self.client.delete(
            view_url.format(username='owner', key=access.key))

        self.assertEqual(response.status_code, 204)
        self.assertFalse(Access.objects.filter(name='access1').exists())


class AdeConfigDetailTestCase(TestCase):

    def test_view(self):
        view_url = '/api/ade_config.json'
        AdeConfig.objects.create(
            ade_url='https://adewebcons-test.unistra.fr/',
            parameters={'projectId': '1'}
        )

        response = self.client.get(view_url)
        data = json.loads(response.content.decode('utf-8'))

        self.assertDictEqual(data, {
            'base_url': 'https://adewebcons-test.unistra.fr/',
            'params': {'projectId': '1'}
        })


class ResourceDetailTestCase(TestCase):

    def test_resource_with_empty_fields(self):
        view_url = '/api/resource/{ext_id}.json'
        Resource.objects.create(ext_id=30622)

        response = self.client.get(view_url.format(ext_id=30622))
        data = json.loads(response.content.decode('utf-8'))

        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(data, {})

    def test_resource_with_fields(self):
        view_url = '/api/resource/{ext_id}.json'
        Resource.objects.create(ext_id=30622, fields={
            'children': [
                {
                    'id': '30628', 'name': 'ESPE COLMAR BATIMENT PRINCIPAL',
                    'has_children': True
                }, {
                    'id': '30623', 'name': 'ESPE COLMAR AILE JOFFRE',
                    'has_children': True
                }, {
                    'id': '30715', 'name': 'Gymnases IUFM COLMAR',
                    'has_children': True
                }
            ]
        })

        response = self.client.get(view_url.format(ext_id=30622))
        data = json.loads(response.content.decode('utf-8'))

        self.assertEqual(response.status_code, 200)
        self.assertListEqual(data['children'], [
            {
                'has_children': True,
                'id': 'https://testserver/api/resource/30623.json/',
                'name': 'ESPE COLMAR AILE JOFFRE'
            }, {
                'has_children': True,
                'id': 'https://testserver/api/resource/30628.json/',
                'name': 'ESPE COLMAR BATIMENT PRINCIPAL'
            }, {
                'has_children': True,
                'id': 'https://testserver/api/resource/30715.json/',
                'name': 'Gymnases IUFM COLMAR'
            }
        ])
