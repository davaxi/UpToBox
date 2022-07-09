import tools
import json


def compute_response(request_event, response_code, response_body=None):
    headers = {}

    if response_body is None:
        response_body = ''

    if type(response_body) is not str:
        headers['Content-Type'] = 'application/json'
        response_body = json.dumps(response_body)

    if 'Origin' in request_event['headers']:
        if request_event['headers']['Origin'] not in tools.constant.ALLOWED_CORS_DOMAINS:
            return {
                'statusCode': tools.constant.STATUS_CODE_UNAUTHORIZED,
                'headers': {},
                'body': ''
            }

        headers['Access-Control-Allow-Origin'] = '*'
        headers['Access-Control-Allow-Credentials'] = 'true'
        headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        headers['Access-Control-Allow-Headers'] = 'authorization'
        headers['Access-Control-Max-Age'] = '86400'

    return {
        'statusCode': response_code,
        'headers': headers,
        'body': response_body
    }
