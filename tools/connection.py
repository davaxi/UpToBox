import os
import pymysql


class Database:

    def __init__(self):
        self.connection = None

    def connected(self):
        return self.connection and self.connection.open

    def connect(self):
        self.connection = pymysql.connect(
            host=os.getenv('MYSQL_HOST'),
            port=int(os.getenv('MYSQL_PORT')),
            user=os.getenv('MYSQL_USER'),
            password=os.getenv('MYSQL_PASSWORD'),
            db=os.getenv('MYSQL_DB'),
            autocommit=True
        )

    def close(self):
        if self.connected():
            try:
                self.connection.close()
            except pymysql.Error:
                pass
        self.connection = None

    def get_cursor(self):
        if not self.connected():
            self.connect()

        return self.connection.cursor()
