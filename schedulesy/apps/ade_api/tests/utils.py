import os
import urllib.parse

from django.conf import settings
from django.test import TestCase
import responses


class ResponsesMixin:
    def setUp(self):
        responses._default_mock.__enter__()
        self.add_default_response()
        super(ResponsesMixin, self).setUp()

    def tearDown(self, *args, **kwargs):
        super(ResponsesMixin, self).tearDown()
        responses._default_mock.__exit__(None, None, None)

    def add_default_response(self):
        """ Override to add default response/s for all test runs """
        raise NotImplementedError


class ADEMixin(ResponsesMixin):

    SESSION_ID = '16d72108506'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.resources_mock = {
            'classroom': 'classroom.xml',
            'instructor': 'instructor.xml',
            'trainee': 'trainee.xml',
            'category5': 'category5.xml'
        }

    def ws_url(self, url_path='', params=None):
        url_path = f'/{url_path}' if url_path else ''
        params = params or {}
        base_url = settings.ADE_WEB_API['HOST']
        query = f'?{urllib.parse.urlencode(params)}' if params else ''
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

        # Get Resources
        for resource, filename in self.resources_mock.items():
            responses.add(
                responses.GET,
                self.ws_url(params={
                    'category': resource,
                    'detail': 3,
                    'tree': True,
                    'hash': True,
                    'function': 'getResources',
                    'sessionId': self.SESSION_ID
                }),
                body=open(os.path.join(
                    os.path.dirname(__file__), 'adews', filename)
                ).read(),
                status=200
            )
