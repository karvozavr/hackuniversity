import re

from flask import Flask, Response, stream_with_context, jsonify, request

from database import Database
from solution.ktetris import KTetris

app = Flask(__name__)


def check_login(login, password, db):
    guard_regex = r"^[A-Za-z0-9_]*$"
    if login is not None and password is not None and re.match(guard_regex, login) and re.match(guard_regex, password):
        result = db.execute(f'SELECT count(*) FROM "user" WHERE id = \'{login}\' AND password = \'{password}\'')
        if result is not None and result[0][0] == 1:
            return True
    return False


@app.route('/check_login')
def check_login_request():
    login = request.headers.get('X-Auth-user-login')
    password = request.headers.get('X-Auth-user-password')

    db = Database()
    if not check_login(login, password, db):
        return "Invalid login/password.", 403
    else:
        return "OK", 200


@app.route('/get')
def get_schedule():
    login = request.headers.get('X-Auth-user-login')
    password = request.headers.get('X-Auth-user-password')

    db = Database()
    if not check_login(login, password, db):
        return "Invalid login/password.", 403

    l = []
    with open('tempfile.bin', 'wb'):
        ktetris = KTetris(Database(), k=300, callback=lambda x: l.append(x))
        ktetris.solve()
    return jsonify(l), 200, {'Access-Control-Allow-Methods': 'POST, GET, OPTIONS', 'Access-Control-Allow-Origin': '*'}
