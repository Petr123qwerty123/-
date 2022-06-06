import datetime
import json

import requests
from requests.structures import CaseInsensitiveDict


class Card:
    def __init__(self):
        self._offset = datetime.timedelta(hours=3)
        self._tz = datetime.timezone(self._offset, name='МСК')

    def identify_qr(self, content):
        url = "https://ChainShopsServer.nikolaipietrov2.repl.co/api/shop/identify_qr"

        headers = CaseInsensitiveDict()
        headers["Content-Type"] = "application/json"
        if len(content) == 16:
            data = {'type': 'accruing_qr',
                    'content': content}

            data = json.dumps(data)
        elif len(content) == 64:
            data = {'type': 'deducting_qr',
                    'content': content}

            data = json.dumps(data)
        else:
            return False
        resp = requests.post(url, headers=headers, data=data)

        result = json.loads(resp.content.decode())

        return result.get('status')

