import unittest
from unittest.mock import Mock, patch

from schedulesy.apps.ade_api.ade import ADEWebAPI


class TestADEWebAPI(unittest.TestCase):
    def setUp(self):
        self.url = 'https://example.com/api'
        self.login = 'reader'
        self.password = 'mylittleponey'
        self.api = ADEWebAPI(self.url, self.login, self.password)

    @patch('requests.get')
    def test_send_request_with_session_id(self, mock_get):
        mock_response = Mock()
        mock_response.text = '<response>data</response>'
        mock_get.return_value = mock_response

        params = {'function': 'test_func', 'sessionId': '12345'}
        self.api._send_request('test_func', **params)

        mock_get.assert_called_once_with(self.api.url, params=params)

    @patch('requests.get')
    def test_send_request_without_session_id(self, mock_get):
        mock_response = Mock()
        mock_response.text = '<response>data</response>'
        mock_get.return_value = mock_response

        params = {'function': 'test_func'}
        self.api.session_id = '12345'
        self.api._send_request('test_func', **params)

        expected_params = {'function': 'test_func', 'sessionId': '12345'}
        mock_get.assert_called_once_with(self.api.url, params=expected_params)

    @patch('requests.get')
    def test_send_request_with_error(self, mock_get):
        mock_response = Mock()
        mock_response.text = '<error>message</error>'
        mock_get.return_value = mock_response

        params = {'function': 'test_func'}
        with self.assertRaises(Exception):
            self.api._send_request('test_func', **params)

    @patch('requests.get')
    def test_send_request_with_empty_response(self, mock_get):
        mock_response = Mock()
        mock_response.text = ''
        mock_get.return_value = mock_response

        params = {'function': 'test_func'}
        with self.assertRaises(Exception):
            self.api._send_request('test_func', **params)
