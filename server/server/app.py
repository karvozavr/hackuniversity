import re

from flask import Flask, Response, stream_with_context, jsonify, request

from database import Database
from solution.ktetris import KTetris

app = Flask(__name__)

DB_NAMES = {'order': '"order"', 'product': 'product', 'equipment': 'equipment', 'eq_hist_data': 'eq_hist_data'}


def check_login(db):
    login = request.headers.get('X-Auth-user-login')
    password = request.headers.get('X-Auth-user-password')

    guard_regex = r"^[A-Za-z0-9_]*$"
    if login is not None and password is not None and re.match(guard_regex, login) and re.match(guard_regex, password):
        result = db.execute(f'SELECT count(*) FROM "user" WHERE id = \'{login}\' AND password = \'{password}\'')
        if result is not None and result[0][0] == 1:
            return True
    return False


@app.route('/check_login')
def check_login_request():
    db = Database()
    if not check_login(db):
        return 'Invalid login/password.', 403
    else:
        return "OK", 200, {'Access-Control-Allow-Methods': 'POST, GET, OPTIONS', 'Access-Control-Allow-Origin': '*'}


def generator(data):
    length = 512
    l = []
    for tup in data:
        print()


@app.route('/get/table')
def get_table():
    db = Database()
    # if not check_login(db):
    #     return 'Invalid login/password.', 403

    table_name = request.args.get('table-name')
    if table_name in DB_NAMES:
        result = db.execute(f'SELECT * FROM {DB_NAMES[table_name]};')
        if result is not None:
            return jsonify(result),

    return "Table not found.", 404


@app.route('/get/schedule')
def get_schedule():
    db = Database()
    if not check_login(db):
        return 'Invalid login/password.', 403

    l = []
    with open('tempfile.bin', 'wb'):
        ktetris = KTetris(Database(), k=300, callback=lambda x: l.append(x))
        ktetris.solve()
    return jsonify(l), 200, {'Access-Control-Allow-Methods': 'POST, GET, OPTIONS', 'Access-Control-Allow-Origin': '*'}
