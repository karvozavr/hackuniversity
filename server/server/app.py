import base64
import os
import re
from enum import Enum
from io import BytesIO
from multiprocessing import Process, Queue

from flask import Flask, Response, jsonify, request, json

from database import Database
from excel import load_equipment_to_database, load_order_to_database, load_product_to_database, load_hist_to_database
from solution.ktetris import KTetris

app = Flask(__name__)

DB_NAMES = {'order': '"order"', 'product': 'product', 'equipment': 'equipment', 'eq_hist_data': 'eq_hist_data'}

HEADERS = {'Access-Control-Allow-Methods': 'POST, GET, OPTIONS', 'Access-Control-Allow-Origin': '*'}

STATIC_STORAGE_NAME = 'static'


class UserType(Enum):
    UNAUTHORIZED = -1
    USER = 0
    ADMIN = 1


def check_login(db):
    login = request.headers.get('X-Auth-user-login')
    password = request.headers.get('X-Auth-user-password')

    guard_regex = r"^[A-Za-z0-9_]*$"
    if login is not None and password is not None and re.match(guard_regex, login) and re.match(guard_regex, password):
        result = db.execute(f'SELECT * FROM "user" WHERE id = \'{login}\' AND password = \'{password}\'')
        if result is not None and len(result) == 1:
            return UserType.ADMIN if result[0][2] == 1 else UserType.USER
    return UserType.UNAUTHORIZED


@app.route('/check_login')
def check_login_request():
    db = Database()
    if check_login(db) is UserType.UNAUTHORIZED:
        return 'Invalid login/password.', 403
    else:
        return "OK", 200, HEADERS


@app.route('/mod')
def modify_table():
    db = Database()
    user = check_login(db)
    if user is not UserType.ADMIN:
        return 'Bad access.', 503

    query = request.args.get('query')
    db.execute(query)


@app.route('/load')
def save_xls_doc():
    db = Database()
    user = check_login(db)
    if user is not UserType.ADMIN:
        return 'Bad access.', 503

    filename = request.args.get('filename')
    b64data = request.get_data(as_text=True)
    b = BytesIO(base64.b64decode(b64data))
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           f'../{STATIC_STORAGE_NAME}/{filename}'), 'wb') as f:
        f.write(b.read())


@app.route('/update_from_files')
def update_from_files():
    db = Database()
    user = check_login(db)
    if user is not UserType.ADMIN:
        return 'Bad access.', 503

    filename = request.args.get('filename')
    table = request.args.get('table')

    if table in DB_NAMES:
        root_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), STATIC_STORAGE_NAME)
        db.execute(f'DROP TABLE IF EXISTS {DB_NAMES[table]};')
        if table == 'order':
            load_order_to_database(db, os.path.join(root_path, filename))
        elif table == 'equipment':
            load_equipment_to_database(db, os.path.join(root_path, filename))
        elif table == 'product':
            load_product_to_database(db, os.path.join(root_path, filename))
        elif table == 'eq_hist_data':
            load_hist_to_database(db, os.path.join(root_path, filename))
        else:
            return 'Not found.', 404
        return 'OK', 200, HEADERS
    return 'Not found', 404


@app.route('/get/table')
def get_table():
    db = Database()
    if check_login(db) is UserType.UNAUTHORIZED:
        return 'Invalid login/password.', 403

    table_name = request.args.get('table')
    if table_name in DB_NAMES:
        result = db.execute(f'SELECT * FROM {DB_NAMES[table_name]};')
        if result is not None:
            return jsonify(result), 200, HEADERS

    return "Table not found.", 404


def generate(queue: Queue, operating):
    yield '['
    while operating[0]:
        try:
            l = []
            for i in range(1000):
                l.append(queue.get(timeout=4))

            yield json.dumps(l) + ','
        except Exception:
            continue
    yield ']'


@app.route('/get/schedule')
def get_schedule():
    db = Database()
    if check_login(db) is UserType.UNAUTHORIZED:
        return 'Invalid login/password.', 403

    l = []
    with open('tempfile.bin', 'wb'):
        queue = Queue()
        operating = [True]
        p = Process(target=solve_problem, args=(lambda x: queue.put(x), operating))
        p.start()
    return Response(generate(queue, operating), content_type='application/json', status=200, headers=HEADERS)


@app.route('/get/top_vulnerable')
def top_vulnerable():
    db = Database()
    if check_login(db) is UserType.UNAUTHORIZED:
        return 'Invalid login/password.', 403

    n = request.args.get('amount')
    result = db.execute(
        'select * from '
        '(select equipment_class, avg(repair) from eq_hist_data GROUP BY equipment_class) as subq '
        f'ORDER BY avg DESC limit {n};')

    if result is not None:
        return jsonify(result), 200, HEADERS
    return "Internal error.", 500


def solve_problem(callback, operating):
    ktetris = KTetris(Database(), k=500, callback=callback)
    ktetris.solve()
    operating[0] = False
