import json

from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Access, LocalCustomization


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
