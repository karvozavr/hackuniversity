import sys

from database import Database
from excel import load_tables_to_database


def main():
    if len(sys.argv) != 2:
        print('Provide 1 argument: excel file')
        exit(1)

    db = Database()
    load_tables_to_database(db)


if __name__ == '__main__':
    sys.argv.append('static/product.xlsx')
    main()
