from functools import partial
import os
import urllib.parse

from django.conf import settings
from django.test import TestCase
import responses

from ..refresh import Refresh


class ResponsesMixin:
    def setUp(self):
        responses.start()
        self.add_default_response()
        super().setUp()

    def tearDown(self):
        super().tearDown()
        responses.stop()
        responses.reset()

    def add_default_response(self):
        """ Override to add default response/s for all test runs """
        raise NotImplementedError


class ADEMixin(ResponsesMixin):

    SESSION_ID = '16d72108506'
    FIXTURES_PATH = os.path.join(os.path.dirname(__file__), 'adews')
    RESOURCES_MOCK = {
        'classroom': 'classroom.xml',
        'instructor': 'instructor.xml',
        'trainee': 'trainee.xml',
        'category5': 'category5.xml'
    }

    def ws_url(self, url_path='', params=None):
        url_path = f'/{url_path}' if url_path else ''
        params = params or {}
        base_url = settings.ADE_WEB_API['HOST']
        query = f'?{urllib.parse.urlencode(params, True)}' if params else ''
        url = '{base_url}{url_path}{query}'.format(**locals())
        return url

    def add_default_response(self):
        # Connection
        responses.add(
            responses.GET,
            self.ws_url(params={
                'login': settings.ADE_WEB_API['USER'],
                'password': settings.ADE_WEB_API['PASSWORD'],
                'function': 'connect'
            }),
            body=f'<session id="{self.SESSION_ID}"/>',
            status=200
        )

        # Set project
        responses.add(
            responses.GET,
            self.ws_url(params={
                'projectId': settings.ADE_WEB_API['PROJECT_ID'],
                'function': 'setProject',
                'sessionId': self.SESSION_ID
            }),
            body=f'<setProject sessionId="{self.SESSION_ID}" '
                 f'projectId="{settings.ADE_WEB_API["PROJECT_ID"]}"/>',
            status=200
        )

    def add_getresources_response(self, *resources):
        resources = resources or self.RESOURCES_MOCK.keys()
        for resource in resources:
            filename = self.RESOURCES_MOCK[resource]
            responses.add(
                responses.GET,
                self.ws_url(params={
                    'category': resource,
                    'detail': 11,
                    'tree': True,
                    'hash': True,
                    'function': 'getResources',
                    'sessionId': self.SESSION_ID
                }),
                body=open(os.path.join(
                    self.FIXTURES_PATH, 'resources', filename)).read(),
                status=200
            )

    def add_getevents_response(self, resource_id):
        responses.add(
            responses.GET,
            self.ws_url(params={
                'resources': resource_id,
                'detail': 0,
                'attribute_filter': Refresh.EVENTS_ATTRIBUTE_FILTERS,
                'function': 'getEvents',
                'sessionId': self.SESSION_ID
            }),
            body=open(os.path.join(
                self.FIXTURES_PATH, 'events', f'resource_{resource_id}.xml')
            ).read(),
            status=200
        )
