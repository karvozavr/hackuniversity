import datetime
import os

import pandas as pd

from database import Database

root_path = os.path.dirname(os.path.abspath(__file__))


def get_path(relpath):
    return os.path.join(root_path, relpath)


def parse_table(filename: str):
    return pd.read_excel(filename, sheet_name=0, header=0)


def load_product_to_database(db: Database, filename=get_path('../static/product.xlsx')):
    data = parse_table(filename)

    for _, row in data.iterrows():
        equipment = '{' + row['equipment_class'].replace('\'', '"')[1:-1] + '}'
        db.insert('product', f"\'{row['_id']}\', \'{equipment}\'", )


def load_order_to_database(db: Database, filename=get_path('../static/order.xlsx')):
    data = parse_table(filename)

    db.copy_from(data, '"order"')


def load_hist_to_database(db: Database, filename=get_path('../static/eq_hist_data.xlsx')):
    data = parse_table(filename)
    data['day'] = data['day'].map(lambda x: str(datetime.datetime.fromtimestamp(x)))
    data = data[['id', 'day', 'work', 'maintenance', 'idle', 'class']]

    db.copy_from(data, 'eq_hist_data')


def load_equipment_to_database(db: Database, filename=get_path('../static/equipment.xlsx')):
    data = parse_table(filename)
    data['available_hours'] = 0

    db.copy_from(data, 'equipment')


def load_tables_to_database(db: Database):
    db.create_schema()
    load_hist_to_database(db)
    load_product_to_database(db)
    load_order_to_database(db)
    load_equipment_to_database(db)
