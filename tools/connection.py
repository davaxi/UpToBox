import os
import psycopg2
from psycopg2.extras import RealDictCursor


class Database:

    def __init__(self):
        self.connection = None

    def connected(self):
        return self.connection and self.connection.closed == 0

    def connect(self):
        self.connection = psycopg2.connect(
            host=os.getenv('PGSQL_HOST'),
            port=os.getenv('PGSQL_PORT'),
            user=os.getenv('PGSQL_USER'),
            password=os.getenv('PGSQL_PASSWORD'),
            database=os.getenv('PGSQL_DB'),
        )
        self.connection.set_session(autocommit=True)

    def close(self):
        if self.connected():
            try:
                self.connection.close()
            except psycopg2.Error:
                pass
        self.connection = None

    def get_cursor(self):
        if not self.connected():
            self.connect()

        return self.connection.cursor(cursor_factory=RealDictCursor)
