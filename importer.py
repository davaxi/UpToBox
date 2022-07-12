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

        print(f"{line['token']} : {line['title']}")

        if result is not None:
            continue

        title_vector = line['title'].replace('.', ' ').replace('-', ' ').replace('_', ' ')
        cursor.execute(
            'INSERT INTO uptobox_link(date, token, title, size, vector) '
            'VALUES(%s, %s, %s, %s, to_tsvector(\'french\', %s))',
            (datetime.now(), line['token'].strip(), line['title'].strip(), int(line['size']) / 1000, title_vector,)
        )