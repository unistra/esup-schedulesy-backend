from django.test import TestCase

from schedulesy.apps.ade_api.models import Resource
from schedulesy.apps.refresh.tasks import _identify_resources


class TaskTestCase(TestCase):
    def setUp(self) -> None:
        r = Resource.objects.create(ext_id='1337')
        Resource.objects.create(ext_id='1338', parent=r)
        Resource.objects.create(
            ext_id='42',
            events={
                'events': [
                    {
                        'id': '1234',
                    }
                ]
            },
        )
        Resource.objects.create(ext_id='421', events={'events': [{'id': '279843'}]})

    def test_identify_resources_with_resource(self):
        data = {
            'operation_id': 'test',
            'events': [{'resources': [1337], 'id': '163477'}],
        }
        result = _identify_resources(data)
        self.assertEqual(len(result), 2)
        self.assertIn('1337', result)

    def test_identify_resources_with_event(self):
        data = {
            'operation_id': 'test',
            'events': [{'resources': ['42'], 'id': '279843'}],
        }
        result = _identify_resources(data)
        self.assertEqual(len(result), 2)
        self.assertIn('421', result)

    def test_identify_resources_missing_resource(self):
        data = {
            'operation_id': 'test',
            'events': [{'resources': ['1977'], 'id': '279843'}],
        }
        result = _identify_resources(data)
        self.assertEqual(len(result), 2)
        self.assertIn('1977', result)
