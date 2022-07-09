import json
import tools

connection = tools.Database()
connection.connect()


def handler(event, context):
    if event['httpMethod'] == 'OPTIONS':
        return tools.compute_response(event, tools.constant.STATUS_CODE_NO_CONTENT, {'status': 'error'})

    if event['httpMethod'] != 'POST':
        return tools.compute_response(event, tools.constant.STATUS_CODE_METHOD_NOT_ALLOWED, {'status': 'error'})

    if event['path'] != '/':
        return tools.compute_response(event, tools.constant.STATUS_CODE_NOT_FOUND, {'status': 'error'})

    try:
        body = json.loads(event['body'])
        if 'key' not in body:
            raise ValueError('Missing key')
        if len(body['key']) != tools.constant.UPTOBOX_TOKEN_LEN:
            raise ValueError('Invalid key len')
        if 'title' not in body:
            raise ValueError('Missing title')
    except ValueError:
        return tools.compute_response(event, tools.constant.STATUS_CODE_BAD_REQUEST, {'status': 'error'})

    cursor = connection.get_cursor()
    cursor.execute("SELECT id FROM uptobox_link WHERE token = %s", (body['key'],))
    result = cursor.fetchone()
    if result is None:
        cursor.execute('INSERT INTO uptobox_link(token, title) VALUES(%s, %s)', (body['key'], body['title']))
    else:
        cursor.execute('UPDATE uptobox_link SET count = count + 1 WHERE id = %s', (result[0], ))

    return tools.compute_response(event, tools.constant.STATUS_CODE_OK, {'status': 'ok'})
