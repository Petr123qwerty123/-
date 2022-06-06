import sqlite3


class Database:
    def __init__(self):
        self._db = './Database/ChainShopsDB.db'

    def set_user(self, name, login, password, reg_dt, card_number):
        conn = sqlite3.connect(self._db)
        cur = conn.cursor()
        query = f"""INSERT INTO customers(login, password, name, registration_dt, card_number) VALUES(?, ?, ?, ?, ?);"""
        values = (login, password, name, reg_dt, card_number)
        cur.execute(query, values)
        conn.commit()

    def check_card_number(self, card_number):
        conn = sqlite3.connect(self._db)
        cur = conn.cursor()
        query = f"""SELECT * FROM customers WHERE card_number=(?);"""
        values = (card_number, )
        cur.execute(query, values)
        result = cur.fetchall()
        conn.commit()
        if len(result) == 0:
            return True
        else:
            return False

    def get_cid(self, card_number):
        conn = sqlite3.connect(self._db)
        cur = conn.cursor()
        query = f"""SELECT cid FROM customers WHERE card_number=(?);"""
        values = (card_number, )
        cur.execute(query, values)
        result = cur.fetchall()
        cid = result[0][0]
        conn.commit()
        return cid

    def check_login_password(self, login, password):
        conn = sqlite3.connect(self._db)
        cur = conn.cursor()
        query = f"""SELECT * FROM customers WHERE login=(?) and password=(?);"""
        values = (login, password)
        cur.execute(query, values)
        result = cur.fetchall()
        conn.commit()
        if len(result) == 0:
            return False
        else:
            return True

    def check_login(self, login):
        conn = sqlite3.connect(self._db)
        cur = conn.cursor()
        query = f"""SELECT * FROM customers WHERE login=(?);"""
        values = (login, )
        cur.execute(query, values)
        result = cur.fetchall()
        conn.commit()
        if len(result) == 0:
            return False
        else:
            return True

    def get_customer_info_by_cid(self, cid):
        conn = sqlite3.connect(self._db)
        cur = conn.cursor()
        query = f"""SELECT * FROM customers WHERE cid=(?);"""
        values = (cid, )
        cur.execute(query, values)
        result = cur.fetchall()
        conn.commit()
        return result

    def get_customer_info_by_login(self, login):
        conn = sqlite3.connect(self._db)
        cur = conn.cursor()
        query = f"""SELECT * FROM customers WHERE login=(?);"""
        values = (login, )
        cur.execute(query, values)
        result = cur.fetchall()
        conn.commit()
        return result

    def set_token(self, cid, token):
        conn = sqlite3.connect(self._db)
        cur = conn.cursor()
        query = f"""UPDATE customers SET token=(?) WHERE cid=(?);"""
        values = (token, cid)
        cur.execute(query, values)
        conn.commit()

    def get_token_by_cid(self, cid):
        conn = sqlite3.connect(self._db)
        cur = conn.cursor()
        query = f"""SELECT token FROM customers WHERE cid=(?);"""
        values = (cid, )
        cur.execute(query, values)
        result = cur.fetchall()
        token = result[0][0]
        conn.commit()
        return token

    def register_activity(self, cid, dt, tid, value=None):
        conn = sqlite3.connect(self._db)
        cur = conn.cursor()
        query = f"""INSERT INTO activities(cid, dt, tid, value) VALUES(?, ?, ?, ?);"""
        values = (cid, dt, tid, value)
        cur.execute(query, values)
        conn.commit()

    def set_confirmation_code(self, cid, confirmation_code):
        conn = sqlite3.connect(self._db)
        cur = conn.cursor()
        query = f"""UPDATE customers SET confirmation_code=(?) WHERE cid=(?);"""
        values = (confirmation_code, cid)
        cur.execute(query, values)
        conn.commit()

    def get_confirmation_code_by_cid(self, cid):
        conn = sqlite3.connect(self._db)
        cur = conn.cursor()
        query = f"""SELECT confirmation_code FROM customers WHERE cid=(?);"""
        values = (cid, )
        cur.execute(query, values)
        result = cur.fetchall()
        code = result[0][0]
        conn.commit()
        return code

    def check_accruing_qr(self, content):
        conn = sqlite3.connect(self._db)
        cur = conn.cursor()
        query = f"""SELECT cid FROM customers WHERE card_number=(?);"""
        values = (content, )
        cur.execute(query, values)
        result = cur.fetchall()
        try:
            cid = result[0][0]
            conn.commit()
            return cid
        except Exception:
            return None

    def check_deducting_qr(self, content):
        conn = sqlite3.connect(self._db)
        cur = conn.cursor()
        query = f"""SELECT cid FROM customers WHERE token=(?);"""
        values = (content, )
        cur.execute(query, values)
        result = cur.fetchall()
        try:
            cid = result[0][0]
            conn.commit()
            return cid
        except Exception:
            return None

    def accrue_deduct(self, cid, value):
        conn = sqlite3.connect(self._db)
        cur = conn.cursor()
        query = f"""UPDATE customers SET scores=scores+(?) WHERE cid=(?);"""
        values = (value, cid)
        cur.execute(query, values)
        conn.commit()

    def get_step(self, ip):
        conn = sqlite3.connect(self._db)
        cur = conn.cursor()
        query = f"""SELECT step FROM client_api_activities WHERE ip=(?);"""
        values = (ip, )
        cur.execute(query, values)
        result = cur.fetchall()
        step = result[0][0]
        conn.commit()
        return step

    def get_cid_ip(self, ip):
        conn = sqlite3.connect(self._db)
        cur = conn.cursor()
        query = f"""SELECT cid FROM client_api_activities WHERE ip=(?);"""
        values = (ip, )
        cur.execute(query, values)
        result = cur.fetchall()
        cid = result[0][0]
        conn.commit()
        return cid

    def get_blocked(self, ip):
        conn = sqlite3.connect(self._db)
        cur = conn.cursor()
        query = f"""SELECT blocked FROM client_api_activities WHERE ip=(?);"""
        values = (ip, )
        cur.execute(query, values)
        result = cur.fetchall()
        blocked = result[0][0]
        conn.commit()
        return blocked

    def get_try(self, ip):
        conn = sqlite3.connect(self._db)
        cur = conn.cursor()
        query = f"""SELECT try FROM client_api_activities WHERE ip=(?);"""
        values = (ip,)
        cur.execute(query, values)
        result = cur.fetchall()
        try_number = result[0][0]
        conn.commit()
        return try_number

    def update_cid(self, ip, new_cid):
        conn = sqlite3.connect(self._db)
        cur = conn.cursor()
        query = f"""UPDATE client_api_activities SET cid=(?), step=(?), try=(?) WHERE ip=(?);"""
        values = (new_cid, 0, 0, ip)
        cur.execute(query, values)
        conn.commit()

    def update_try(self, ip):
        conn = sqlite3.connect(self._db)
        cur = conn.cursor()
        query = f"""UPDATE client_api_activities SET try=try+1 WHERE ip=(?);"""
        values = (ip, )
        cur.execute(query, values)
        conn.commit()

    def update_step(self, ip, new_step):
        conn = sqlite3.connect(self._db)
        cur = conn.cursor()
        query = f"""UPDATE client_api_activities SET step=(?), try=(?) WHERE ip=(?);"""
        values = (new_step, 0, ip)
        cur.execute(query, values)
        conn.commit()

    def to_block(self, ip):
        conn = sqlite3.connect(self._db)
        cur = conn.cursor()
        query = f"""UPDATE client_api_activities SET blocked=(?) WHERE ip=(?);"""
        values = (True, ip)
        cur.execute(query, values)
        conn.commit()

    def register_ip(self, ip):
        conn = sqlite3.connect(self._db)
        cur = conn.cursor()
        query = f"""INSERT INTO client_api_activities(ip) VALUES(?);"""
        values = (ip, )
        cur.execute(query, values)
        conn.commit()

    def check_ip(self, ip):
        conn = sqlite3.connect(self._db)
        cur = conn.cursor()
        query = f"""SELECT ip FROM client_api_activities WHERE ip=(?);"""
        values = (ip, )
        cur.execute(query, values)
        result = cur.fetchall()
        conn.commit()
        return result
