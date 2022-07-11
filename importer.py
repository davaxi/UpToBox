import csv
import tools
from datetime import datetime

connection = tools.Database()
connection.connect()

cursor = connection.get_cursor()

fieldnames = ['token', 'title', 'size']
with open('data.csv', 'r') as file_csv:
    reader = csv.DictReader(file_csv)

    for line in reader:
        cursor.execute("SELECT id, like_count FROM uptobox_link WHERE enabled = true AND token = %s", (line['token'],))
        result = cursor.fetchone()

        if result is None:
            title_vector = line['title'].replace('.', ' ').replace('-', ' ').replace('_', ' ')
            cursor.execute(
                'INSERT INTO uptobox_link(date, token, title, size, vector) '
                'VALUES(%s, %s, %s, %s, to_tsvector(\'french\', %s))',
                (datetime.now(), line['token'].strip(), line['title'].strip(), int(line['size']) / 1000, title_vector,)
            )
            continue

        like_count = result['like_count'] + 2
        cursor.execute('UPDATE uptobox_link SET like_count = %s WHERE id = %s', (like_count, result['id'],))

    print(line['token'])
