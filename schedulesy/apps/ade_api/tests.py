import unittest
from unittest import mock


# from django.test import TestCase
#
# # Create your tests here.
# from schedulesy.apps.ade_api.ade import Config, ADEWebAPI
#
#
# def mocked_requests_get(*args, **kwargs):
#     class MockResponse:
#         def __init__(self, json_data, status_code):
#             self.json_data = json_data
#             self.status_code = status_code
#
#         def json(self):
#             return self.json_data
#
#     if args[0] == 'https://adeweb.unistra.fr/jsp/webapi':
#         return MockResponse({"key1": "value1"}, 200)
#     elif args[0] == 'http://someotherurl.com/anothertest.json':
#         return MockResponse({"key2": "value2"}, 200)
#
#     return MockResponse(None, 404)
#
#
# # Our test case class
# class AdeTestCase(TestCase):
#
#     # We patch 'requests.get' with our own method. The mock object is passed in to our test case method.
#     @mock.patch('schedulesy.apps.ade_api.ade.requests.get', side_effect=mocked_requests_get)
#     def test_fetch(self, mock_get):
#         config = Config.create(url='https://adeweb.unistra.fr/jsp/webapi', login='toto',
#                                password='toto')
#         myade = ADEWebAPI(**config)
