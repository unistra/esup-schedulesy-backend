from django.contrib.auth import get_user_model
from django.http import HttpRequest
from django.test import TestCase

from schedulesy.apps.ade_api.models import Access, Customization
from ..views import IsOwnerPermission


User = get_user_model()


class IsOwnerPermissionTestCase(TestCase):

    def setUp(self):
        super().setUp()
        self.request = HttpRequest()
        self.user_owner = User.objects.create_user('owner')

    def test_is_owner(self):
        self.request.user = self.user_owner
        customization = Customization(username=self.user_owner.username)

        self.assertTrue(IsOwnerPermission().has_object_permission(
            self.request, None, customization))

    def test_is_not_owner(self):
        self.request.user = self.user_owner
        customization = Customization(username='not-owner')

        self.assertFalse(IsOwnerPermission().has_object_permission(
            self.request, None, customization))

    def test_is_superuser(self):
        superuser = User.objects.create_superuser(
            'super', 'super@no-reply.com', 'pass')
        self.request.user = superuser
        customization = Customization(username='not-owner')

        self.assertTrue(IsOwnerPermission().has_object_permission(
            self.request, None, customization))

    def test_with_other_username_field(self):
        customization = Customization.objects.create(
            username=self.user_owner.username)
        access = Access(name='access1', customization=customization)

        self.assertTrue(
            IsOwnerPermission('customization__username').has_object_permission(
                self.request, None, access))
