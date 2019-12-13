from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework_simplejwt.exceptions import (
    AuthenticationFailed, InvalidToken,
)
from rest_framework_simplejwt.settings import api_settings

from ..authentication import CustomJWTAuthentication


User = get_user_model()


class CustomJWTAuthenticationTestCase(TestCase):

    def setUp(self):
        super().setUp()
        self.backend = CustomJWTAuthentication()

    def test_get_user(self):
        payload = {'some_other_id': 'foo'}
        jwt_settings = dict(settings.SIMPLE_JWT)

        # Should raise error if no recognizable user identification
        with self.assertRaises(InvalidToken):
            self.backend.get_user(payload)

        payload[api_settings.USER_ID_CLAIM] = 'jwt_user'

        # Raise an exception if user not found and CREATE_USER is set to False
        jwt_settings['CREATE_USER'] = False
        with self.settings(SIMPLE_JWT=jwt_settings):
            with self.assertRaises(AuthenticationFailed) as af:
                self.backend.get_user(payload)
            self.assertEqual(af.exception.detail['code'], 'user_not_found')

            user = User.objects.create_user(username='jwt_user')
            user.is_active = False
            user.save()

            # Should raise exception if user is inactive
            with self.assertRaises(AuthenticationFailed) as af:
                self.backend.get_user(payload)
            self.assertEqual(af.exception.detail['code'], 'user_inactive')

            user.is_active = True
            user.save()

            # Otherwise, should return correct user
            self.assertEqual(self.backend.get_user(payload).id, user.id)

        # And should create an user if it does not exist and CREATE_USER is set
        # to True
        payload[api_settings.USER_ID_CLAIM] = 'jwt_new_user'
        jwt_settings['CREATE_USER'] = True
        with self.settings(SIMPLE_JWT=jwt_settings):
            self.assertEqual(getattr(self.backend.get_user(payload),
                                     api_settings.USER_ID_FIELD),
                             'jwt_new_user')

            # The user should not be recreated
            self.assertEqual(getattr(self.backend.get_user(payload),
                                     api_settings.USER_ID_FIELD),
                             'jwt_new_user')
