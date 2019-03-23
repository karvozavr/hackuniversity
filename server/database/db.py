import psycopg2


class Database:

    def __init__(self):
        try:
            self.connection = psycopg2.connect(dbname='biocadproduction',
                                               user='postgres',
                                               host='localhost',
                                               pasword=None,
                                               port='5432')
        except Exception as e:
            print('Failed to connect to database with exception: ', e)

    def insert(self, table: str, value: str):
        with self.connection.cursor() as curs:
            curs.execute(f'INSERT INTO {table} VALUES ({value})')

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
                pass

            return result


def create_schema(db: Database):
    with open('static/schema.sql', 'r') as schema:
        schema_str = schema.read()
        db.execute(schema_str)
        db.connection.commit()
