import os
import tools
import string
from datetime import datetime
from flask import Flask, render_template, request

connection = tools.Database()
connection.connect()

app = Flask(__name__)


@app.route("/", methods=['GET'])
def index():
    data = {'ping': 'pong'}

    cursor = connection.get_cursor()
    cursor.execute('SELECT COUNT(*) as count, SUM(size) as total FROM uptobox_link WHERE enabled = true')
    row = cursor.fetchone()

    letters = [letter for letter in string.ascii_uppercase]

    archive_size = 0
    if os.path.isfile(tools.constant.ARCHIVE_PATH):
        stats = os.stat(tools.constant.ARCHIVE_PATH)
        archive_size = stats.st_size

    return render_template(
        'index.html',
        token=tools.security.jwt_encode(data),
        count=row['count'],
        totalSize=row['total'],
        archiveSize=archive_size,
        letters=letters,
    )


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

    start_withs = [letter for letter in string.ascii_uppercase]
    start_withs.append('number')

    query = request.args.get('q', '')
    sort = request.args.get('sort', '')
    order = request.args.get('order', '')
    start_with = request.args.get('start-with')
    if sort not in ['id', 'title', 'size', 'like_count']:
        sort = 'id'
    if order not in ['asc', 'desc']:
        order = 'desc'
    if start_with not in start_withs:
        start_with = ''

    params = ()
    sql = 'SELECT id, token, title, size, like_count FROM uptobox_link WHERE enabled = true'
    if query:
        sql = f'{sql} AND vector @@ websearch_to_tsquery(\'french\', %s)'
        params = params + (query, )
    if start_with:
        sql = f'{sql} AND SUBSTR(title, 1, 1) =ANY(%s)'
        if start_with == 'number':
            params = params + ([digit for digit in string.digits], )
        else:
            params = params + ([start_with.lower(), start_with.upper()], )

    sql = f'{sql} ORDER BY {sort} {order} LIMIT 100'

    cursor = connection.get_cursor()
    cursor.execute(sql, params)

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
