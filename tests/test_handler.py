import json
import unittest

import tools.constant
from tools import constant
from handler import handler

connection = tools.Database()
connection.connect()


class TestHandler(unittest.TestCase):

    def test_invalid_cors(self):
        response = handler(
            {
                'headers': {'Origin': 'invalid_origin'},
                'body': '',
                'event': '',
                'httpMethod': 'OPTIONS',
                'path': '/'
            },
            {'test': True}
        )
        self.assertIn('statusCode', response)
        self.assertIn('headers', response)
        self.assertIn('body', response)
        self.assertEqual(response['statusCode'], constant.STATUS_CODE_UNAUTHORIZED)
        self.assertEqual('', response['body'])

    def test_invalid_method(self):
        response = handler(
            {
                'headers': {'Origin': tools.constant.ALLOWED_CORS_DOMAINS[0]},
                'body': '',
                'event': 'GET',
                'httpMethod': '',
                'path': '/'
            },
            {'test': True}
        )
        self.assertIn('headers', response)

        self.assertIn('statusCode', response)
        self.assertEqual(response['statusCode'], constant.STATUS_CODE_METHOD_NOT_ALLOWED)

        self.assertIn('body', response)
        body = json.loads(response['body'])
        self.assertIn('status', body)
        self.assertEqual('error', body['status'])

    def test_invalid_path(self):
        response = handler(
            {
                'headers': {'Origin': tools.constant.ALLOWED_CORS_DOMAINS[0]},
                'body': '',
                'event': '',
                'httpMethod': 'POST',
                'path': '/invalid_path'
            },
            {'test': True}
        )

        self.assertIn('headers', response)

        self.assertIn('statusCode', response)
        self.assertEqual(response['statusCode'], constant.STATUS_CODE_NOT_FOUND)

        self.assertIn('body', response)
        body = json.loads(response['body'])
        self.assertIn('status', body)
        self.assertEqual('error', body['status'])

    def test_valid_cors(self):
        response = handler(
            {
                'headers': {'Origin': tools.constant.ALLOWED_CORS_DOMAINS[0]},
                'body': '',
                'event': '',
                'httpMethod': 'OPTIONS',
                'path': ''
            },
            {'test': True}
        )
        self.assertIn('headers', response)
        self.assertIn('Access-Control-Allow-Origin', response['headers'])
        self.assertEqual(response['headers']['Access-Control-Allow-Origin'], '*')
        self.assertIn('Access-Control-Allow-Credentials', response['headers'])
        self.assertEqual(response['headers']['Access-Control-Allow-Credentials'], 'true')

        self.assertIn('statusCode', response)
        self.assertEqual(response['statusCode'], constant.STATUS_CODE_NO_CONTENT)

        self.assertIn('body', response)
        self.assertIn('', response['body'])

    def test_invalid_body(self):
        response = handler(
            {
                'headers': {'Origin': tools.constant.ALLOWED_CORS_DOMAINS[0]},
                'body': '{}',
                'event': '',
                'httpMethod': 'POST',
                'path': '/'
            },
            {'test': True}
        )
        self.assertIn('statusCode', response)
        self.assertEqual(response['statusCode'], constant.STATUS_CODE_BAD_REQUEST)

        self.assertIn('body', response)
        body = json.loads(response['body'])
        self.assertIn('status', body)
        self.assertEqual('error', body['status'])

    def test(self):
        key = 'XXXXXXXXXXXX'
        body = {'key': key, 'title': 'My title'}
        response = handler(
            {
                'headers': {'Origin': tools.constant.ALLOWED_CORS_DOMAINS[0]},
                'body': json.dumps(body),
                'event': '',
                'httpMethod': 'POST',
                'path': '/'
            },
            {'test': True}
        )
        self.assertIn('statusCode', response)
        self.assertEqual(response['statusCode'], constant.STATUS_CODE_OK)

        self.assertIn('body', response)
        body = json.loads(response['body'])
        self.assertIn('status', body)
        self.assertEqual('ok', body['status'])

        connection.get_cursor().execute('DELETE FROM uptobox_link WHERE token = %s', (key, ))
