import json

from flask import Flask, request, url_for, redirect
from threading import Thread
import datetime

from Modules.Card import Card

app = Flask('')

card = Card()

offset = datetime.timedelta(hours=3)
tz = datetime.timezone(offset, name='МСК')


# @app.route('/')
# def main():
#     return redirect(url_for('new_cheque'))
#
#
# @app.route('/api/shop/new_cheque')
# def new_cheque():
#     cheque.new_cheque()
#     response = {'status': True}
#     response = json.dumps(response)
#     return response
#
#
# @app.route('/api/shop/product', methods=['POST'])
# def pick_product():
#     gid = request.json.get('content')
#     cheque.edit_cheque(gid)
#     return ''


@app.route('/api/shop/card', methods=['POST'])
def peep_card():
    content = request.json.get('content')
    result = card.identify_qr(content)
    if result:
        response = {'status': True}
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
