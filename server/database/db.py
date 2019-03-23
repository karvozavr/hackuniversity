import io
import os

import pandas as pd

import psycopg2


class Database:

    def __init__(self):
        try:
            dir = os.path.abspath(os.path.dirname(__file__))
            with open(os.path.join(dir, '../dbconnect'), 'r') as dbconnect:
                host = dbconnect.readline().strip()
                passwd = dbconnect.readline().strip()

            self.connection = psycopg2.connect(dbname='biotech',
                                               user='biotech',
                                               host=host,
                                               password=passwd,
                                               port='5432')
        except Exception as e:
            print('Failed to connect to database with exception: ', e)

    def insert(self, table: str, value: str):
        with self.connection.cursor() as curs:
            try:
                curs.execute(f'INSERT INTO {table} VALUES ({value})')
            except Exception as e:
                print('Execution failed:')
                print(e)
            self.connection.commit()

    def execute(self, command: str):
        with self.connection.cursor() as cursor:
            try:
                cursor.execute(command)
            except Exception as e:
                print('Execution failed:')
                print(e)

            result = None
            try:
                result = cursor.fetchall()
            except Exception as e:
                self.connection.commit()

            return result

    def copy_from(self, data: pd.DataFrame, table: str):
        output = io.StringIO()
        data.to_csv(output, sep='\t', header=False, index=False)
        output.seek(0)

        try:
            with self.connection.cursor() as cursor:
                cursor.copy_from(output, table, null='NULL', sep='\t')
        except Exception as e:
            print('Failed to copy data to database.')
            print(e)

        self.connection.commit()

    def create_schema(self):
        with open('../static/schema.sql', 'r') as schema:
            schema_str = schema.read()
            self.execute(schema_str)
            self.connection.commit()
