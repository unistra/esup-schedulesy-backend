from django.test import TestCase
from django.db.utils import IntegrityError

from ..models import AdeConfig


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
