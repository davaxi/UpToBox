import os
import tools
from datetime import datetime
from flask import Flask, render_template, request

connection = tools.Database()
connection.connect()

app = Flask(__name__)


@app.route("/", methods=['GET'])
def index():
    data = {'ping': 'pong'}

    cursor = connection.get_cursor()
    cursor.execute('SELECT COUNT(*) as count FROM uptobox_link WHERE enabled = true')
    row = cursor.fetchone()

    return render_template('index.html', token=tools.security.jwt_encode(data), count=row['count'])


@app.route("/like", methods=['POST'])
def like_link():
    authorization = request.headers.get('Authorization', '')
    token = tools.security.get_token(authorization)
    data = tools.security.jwt_decode(token)
    if data is None:
        return {"status": "unauthorized"}

    data = request.get_json()
    if 'id' not in data:
        return {"status": "invalid_data"}
    if 'action' not in data:
        return {"status": "invalid_data"}
    elif data['action'] not in ['up', 'down']:
        return {"status": "invalid_data"}

    cursor = connection.get_cursor()
    cursor.execute("SELECT id, like_count FROM uptobox_link WHERE enabled = true AND id = %s", (data['id'],))
    result = cursor.fetchone()
    if result is None:
        return {"status": "invalid_data"}

    like_count = result['like_count']
    if data['action'] == 'up':
        like_count = like_count + 1
    else:
        like_count = like_count - 1

    cursor.execute('UPDATE uptobox_link SET like_count = %s WHERE id = %s', (like_count, result['id'],))

    return {"status": "ok", "like_count": like_count}


@app.route("/add", methods=['POST'])
def add_url():
    authorization = request.headers.get('Authorization', '')
    token = tools.security.get_token(authorization)
    data = tools.security.jwt_decode(token)
    if data is None:
        return {"status": "unauthorized"}

    data = request.get_json()
    if 'token' not in data:
        return {"status": "invalid_data"}
    elif len(data['token']) < 1 or len(data['token']) > tools.constant.UPTOBOX_TOKEN_LEN:
        return {"status": "invalid_data"}
    if 'title' not in data or not data['title']:
        return {"status": "invalid_data"}
    if 'size' not in data or not data['size'] or not isinstance(data['size'], int):
        return {"status": "invalid_data"}

    cursor = connection.get_cursor()
    cursor.execute("SELECT id, like_count FROM uptobox_link WHERE enabled = true AND token = %s", (data['token'],))
    result = cursor.fetchone()
    if result is None:
        title_vector = data['title'].replace('.', ' ').replace('-', ' ').replace('_', ' ')
        cursor.execute(
            'INSERT INTO uptobox_link(date, token, title, size, vector) '
            'VALUES(%s, %s, %s, %s, to_tsvector(\'french\', %s))',
            (datetime.now(), data['token'].strip(), data['title'].strip(), data['size'] / 1000, title_vector,)
        )
    else:
        like_count = result['like_count'] + 2
        cursor.execute('UPDATE uptobox_link SET like_count = %s WHERE id = %s', (like_count, result['id'],))

    return {"status": "ok"}


@app.route("/search", methods=['GET'])
def search():
    authorization = request.headers.get('Authorization', '')
    token = tools.security.get_token(authorization)
    data = tools.security.jwt_decode(token)
    if data is None:
        return {"status": "unauthorized"}

    query = request.args.get('q', '')
    sort = request.args.get('sort', '')
    order = request.args.get('order', '')
    if sort not in ['id', 'title', 'size']:
        sort = 'id'
    if order not in ['asc', 'desc']:
        order = 'desc'

    cursor = connection.get_cursor()
    if not query:
        cursor.execute(
            'SELECT id, token, title, size, like_count '
            'FROM uptobox_link '
            'WHERE enabled = true '
            f'ORDER BY {sort} {order} '
            'LIMIT 100'
        )
    else:
        cursor.execute(
            'SELECT id, token, title, size, like_count '
            'FROM uptobox_link '
            'WHERE enabled = true '
            'AND vector @@ websearch_to_tsquery(\'french\', %s) '
            f'ORDER BY {sort} {order} '
            f'LIMIT 100',
            (query, )
        )

    items = []
    for item in cursor.fetchall():
        items.append({
            'id': item['id'],
            'title': item['title'],
            'size': item['size'] * 1000,
            'like_count': item['like_count'],
            'link': 'https://uptobox.com/' + item['token'],
        })

    return {"status": "ok", "items": items}


if __name__ == "__main__":
    port = int(os.environ.get('FLASK_PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
