import datetime

import pandas as pd

from database import Database


def parse_table(filename: str):
    return pd.read_excel(filename, sheet_name=0, header=0)


def load_product_to_database(db: Database):
    data = parse_table('../static/product.xlsx')

    for _, row in data.iterrows():
        equipment = '{' + row['equipment_class'].replace('\'', '"')[1:-1] + '}'
        db.insert('product', f"\'{row['_id']}\', \'{equipment}\'", )


def load_order_to_database(db: Database):
    data = parse_table('../static/order.xlsx')

    db.copy_from(data, '"order"')


def load_hist_to_database(db: Database):
    data = parse_table('../static/eq_hist_data.xlsx')
    data['day'] = data['day'].map(lambda x: str(datetime.datetime.fromtimestamp(x)))
    data = data[['id', 'day', 'work', 'maintenance', 'idle', 'class']]

    db.copy_from(data, 'eq_hist_data')


def load_equipment_to_database(db: Database):
    data = parse_table('../static/equipment.xlsx')
    data['available_hours'] = 0

    db.copy_from(data, 'equipment')


def load_tables_to_database(db: Database):
    db.create_schema()
    load_hist_to_database(db)
    load_product_to_database(db)
    load_order_to_database(db)
    load_equipment_to_database(db)
