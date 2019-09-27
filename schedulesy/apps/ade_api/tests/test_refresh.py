from django.test import TestCase

from .utils import ADEMixin
from ..models import Resource
from ..refresh import Refresh


class RefreshTestCase(ADEMixin, TestCase):

    def test_initial_classroom_refresh(self):
        refresh = Refresh()
        refresh.refresh_category('classroom')

        self.assertEqual(Resource.objects.count(), 19)
