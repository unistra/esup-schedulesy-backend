from django.contrib.auth import get_user_model
from django.http import HttpRequest
from django.test import TestCase

from ..permissions import IsOwnerPermission
from .models import Info, Profile

User = get_user_model()


class IsOwnerPermissionTestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.request = HttpRequest()
        self.user_owner = User.objects.create_user('owner')

    def test_is_owner(self):
        self.request.user = self.user_owner
        profile = Profile(username=self.user_owner.username)

        self.assertTrue(
            IsOwnerPermission().has_object_permission(self.request, None, profile)
        )

    def test_is_not_owner(self):
        self.request.user = self.user_owner
        profile = Profile(username='not-owner')

        self.assertFalse(
            IsOwnerPermission().has_object_permission(self.request, None, profile)
        )

    def test_is_superuser(self):
        superuser = User.objects.create_superuser('super', 'super@no-reply.com', 'pass')
        self.request.user = superuser
        profile = Profile(username='not-owner')

        self.assertTrue(
            IsOwnerPermission().has_object_permission(self.request, None, profile)
        )

    def test_with_other_username_field(self):
        profile = Profile.objects.create(
            name='profile1', username=self.user_owner.username
        )
        info = Info(profile=profile)
        self.request.user = self.user_owner

        self.assertTrue(
            IsOwnerPermission('profile__username').has_object_permission(
                self.request, None, info
            )
        )
