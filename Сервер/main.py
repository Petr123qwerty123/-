from flask import Flask, request, abort
from threading import Thread
import datetime
import json
from Modules.Customer import Customer


app = Flask('')

offset = datetime.timedelta(hours=3)
tz = datetime.timezone(offset, name='МСК')

customer = Customer()


def get_ip_addr():
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        ip_addr = request.environ['REMOTE_ADDR']
    else:
        ip_addr = request.environ['HTTP_X_FORWARDED_FOR']
    return ip_addr


@app.route('/api/client/registration', methods=['POST'])
def registration():
    step = 1
    name = request.json.get('name')
    password = request.json.get('password')
    email = request.json.get('email')
    cid = customer.registration(name, email, password)
    if customer.check_request(get_ip_addr(), cid, step):
        if cid:
            name, scores, qr = customer.get_info_by_cid(cid)
            response = {'status': True, 'name': name, 'scores': scores, 'qr': qr, 'cid': cid}
        else:
            response = {'status': False}
        response = json.dumps(response)
        return response
    else:
        abort(403)


@app.route('/api/client/auth', methods=['POST'])
def auth():
    step = 2
    login = request.json.get('login')
    password = request.json.get('password')
    cid, *other_info = customer.get_info_by_login(login)
    if customer.check_request(get_ip_addr(), cid, step):
        if customer.check_login_password(login, password):
            response = {'status': True}
            customer.send_code(login)
        else:
            response = {'status': False}
        response = json.dumps(response)
        return response
    else:
        abort(403)


@app.route('/api/client/code', methods=['POST'])
def code():
    step = 3
    code = request.json.get('code')
    email = request.json.get('email')
    cid, name, scores, qr = customer.get_info_by_login(email)
    if customer.check_request(get_ip_addr(), cid, step):
        if code == customer.get_confirmation_code(cid):
            customer.clear_confirmation_code(cid)
            response = {'status': True, 'name': name, 'scores': scores, 'qr': qr, 'cid': cid}
        else:
            customer.send_code(email)
            response = {'status': False}
        response = json.dumps(response)
        return response
    else:
        abort(403)


@app.route('/api/client/deduction_qr', methods=['POST'])
def deduction_qr():
    step = 4
    cid = request.json.get('cid')
    if customer.check_request(get_ip_addr(), cid, step):
        last_token = customer.get_token(cid)
        activity = {'cid': cid, 'tid': 4, 'dt': datetime.datetime.now(tz=tz)}
        customer.register_activity(activity)
        token = customer.update_token(cid, last_token, activity)
        qr = customer.get_qr(token)
        response = {'qr': qr}
        response = json.dumps(response)
        return response
    else:
        abort(403)


@app.route('/api/client/logout', methods=['POST'])
def logout():
    step = 5
    cid = request.json.get('cid')
    if customer.check_request(get_ip_addr(), cid, step):
        last_token = customer.get_token(cid)
        activity = {'cid': cid, 'tid': -1, 'dt': datetime.datetime.now(tz=tz)}
        customer.update_token(cid, last_token, activity)
        response = {'status': True}
        response = json.dumps(response)
        return response
    else:
        abort(403)


@app.route('/api/client/user_info', methods=['POST'])
def user_info():
    step = 6
    cid = request.json.get('cid')
    if customer.check_request(get_ip_addr(), cid, step):
        try:
            name, scores, qr = customer.get_info_by_cid(cid)
            response = {'status': True, 'scores': scores, 'name': name, 'qr': qr}
        except Exception:
            response = {'status': False}
        response = json.dumps(response)
        return response
    else:
        abort(403)


@app.route('/api/shop/identify_qr', methods=['POST'])
def identify_qr():
    type = request.json.get('type')
    content = request.json.get('content')
    if type == 'accruing_qr':
        result = customer.check_accruing_qr(content)
        if result is not None:
            cid = int(result)
            value = 100
            last_token = customer.get_token(cid)
            activity = {'cid': cid, 'tid': 1, 'dt': datetime.datetime.now(tz=tz)}
            customer.register_activity(activity)
            customer.update_token(cid, last_token, activity)
            activity = {'cid': cid, 'tid': 2, 'dt': datetime.datetime.now(tz=tz), 'value': value}
            customer.register_activity(activity)
            customer.accrue_deduct(cid, value)
            customer.update_token(cid, last_token, activity)
            response = {'status': True}
        else:
            response = {'status': False}
    elif type == 'deducting_qr':
        result = customer.check_deducting_qr(content)
        if result is not None:
            cid = int(result)
            value = -100
            last_token = customer.get_token(cid)
            activity = {'cid': cid, 'tid': 1, 'dt': datetime.datetime.now(tz=tz)}
            customer.register_activity(activity)
            customer.update_token(cid, last_token, activity)
            activity = {'cid': cid, 'tid': 3, 'dt': datetime.datetime.now(tz=tz), 'value': value}
            customer.register_activity(activity)
            customer.accrue_deduct(cid, value)
            customer.update_token(cid, last_token, activity)
            response = {'status': True, 'cid': result}
        else:
            response = {'status': False}
    else:
        response = {'status': False}
    response = json.dumps(response)
    return response


def run():
    app.run(host="0.0.0.0", port=5000)


def keep_alive():
    server = Thread(target=run)
    server.start()


while True:
    run()