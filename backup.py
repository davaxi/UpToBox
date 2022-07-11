import os
import csv
import tools

if not os.path.isdir(tools.constant.ARCHIVE_FOLDER):
    os.mkdir(tools.constant.ARCHIVE_FOLDER)

connection = tools.Database()
connection.connect()

cursor = connection.get_cursor()
cursor.execute(
    'SELECT '
    '   id as id, '
    '   \'https://uptobox.com/\' || token as link, '
    '   title as title, '
    '   size as size, '
    '   like_count as like_count '
    'FROM uptobox_link '
    'WHERE enabled = true AND exported = false ORDER BY id')
rows = cursor.fetchall()

ids = []
fieldnames = ['id', 'link', 'title', 'size', 'like_count']
with open(tools.ARCHIVE_PATH, 'a', encoding='UTF8') as file:

    writer = csv.DictWriter(file, fieldnames=fieldnames)
    # writer.writeheader()
    for row in rows:
        row['size'] = row['size'] * 1000
        writer.writerow(row)
        ids.append(row['id'])

cursor.execute('UPDATE uptobox_link SET exported = TRUE WHERE id =ANY(%s)', (ids, ))