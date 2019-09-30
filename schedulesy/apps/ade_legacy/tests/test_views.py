import json

from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Customization


User = get_user_model()


class CustomizationListTestCase(TestCase):

    def setUp(self):
        super().setUp()
        self.view_url = '/legacy/customization.json'

    def tearDown(self):
        super().tearDown()
        Customization.objects.all().delete()

    def test_list_customizations_with_owner(self):
        Customization.objects.create(id=1, directory_id='1', username='owner')
        Customization.objects.create(
            id=2, directory_id='2', username='not_owner')
        User.objects.create_user('owner', password='pass')

        self.client.login(username='owner', password='pass')
        response = self.client.get(self.view_url)
        data = json.loads(response.content.decode('utf-8'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['id'], 1)

    def test_list_customizations_with_superuser(self):
        Customization.objects.create(id=1, directory_id='1', username='user1')
        Customization.objects.create(id=2, directory_id='2', username='user2')
        User.objects.create_superuser('super', 'super@no-reply.com', 'pass')

        self.client.login(username='super', password='pass')
        response = self.client.get(self.view_url)
        data = json.loads(response.content.decode('utf-8'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 2)

    def test_post_customization_new_object(self):
        response = self.client.post(
            self.view_url, {'directory_id': 1, 'username': 'owner'})

        self.assertEqual(response.status_code, 201)
        self.assertTrue(
            Customization.objects.get(directory_id=1, username='owner'))

    def test_post_customization_existing_object(self):
        Customization.objects.create(id=1, directory_id='1', username='owner')
        User.objects.create_user('owner', password='pass')

        self.client.login(username='owner', password='pass')
        response = self.client.post(
            self.view_url, {'directory_id': 1, 'username': 'owner'})

        self.assertEqual(response.status_code, 409)
