import datetime
import smtplib

from Database.Database import Database
import hashlib
import random
from password_strength import PasswordPolicy, PasswordStats


class Customer:
    def __init__(self):
        self._db = Database()
        self._password_policy = PasswordPolicy.from_names(length=8,
                                                          uppercase=2,
                                                          numbers=2,
                                                          special=2,
                                                          nonletters=2)
        self._offset = datetime.timedelta(hours=3)
        self._tz = datetime.timezone(self._offset, name='МСК')

    def _check_password_reliability(self, password):
        if len(self._password_policy.test(password)) == 0:
            stats = PasswordStats(password)
            if stats.strength() >= 0.8:
                check_result = True
            else:
                check_result = False
        else:
            check_result = False
        return check_result

    def _generate_new_card_number(self):
        card_number = random.randint(1000000000000000, 9999999999999999)
        while not self._db.check_card_number(card_number):
            card_number = random.randint(1000000000000000, 9999999999999999)
        return card_number

    def registration(self, name, login, password):
        if self.check_login(login):
            return False
        else:
            if self._check_password_reliability(password):
                card_number = self._generate_new_card_number()
                reg_dt = datetime.datetime.now(tz=self._tz)
                self._db.set_user(name, login, password, reg_dt, card_number)
                cid = self._db.get_cid(card_number)
                token = self._generate_new_token([cid, login, password, name, reg_dt, card_number])
                self._db.set_token(cid, token)
                return cid
            else:
                return False

    def get_info_by_cid(self, cid):
        info = self._db.get_customer_info_by_cid(cid)
        name = info[0][3]
        scores = info[0][6]
        card_number = info[0][7]
        qr = self.get_qr(card_number)
        return name, scores, qr

    def get_info_by_login(self, login):
        info = self._db.get_customer_info_by_login(login)
        cid = info[0][0]
        name = info[0][3]
        scores = info[0][6]
        card_number = info[0][7]
        qr = self.get_qr(card_number)
        return cid, name, scores, qr

    def check_login_password(self, login, password):
        return self._db.check_login_password(login, password)

    def check_login(self, login):
        return self._db.check_login(login)

    def _generate_new_token(self, data):
        h = hashlib.sha256()
        for i in range(len(data)):
            data_bytes = str(data[i]).encode('utf-8')
            h.update(data_bytes)
        token = h.hexdigest()
        return token

    def update_token(self, cid, last_token, activity):
        data = list(activity.values())
        h = hashlib.sha256(last_token.encode('utf-8'))
        for i in range(len(data)):
            data_bytes = str(data[i]).encode('utf-8')
            h.update(data_bytes)
        token = h.hexdigest()
        self._db.set_token(cid, token)
        return token

    def get_token(self, cid):
        return self._db.get_token_by_cid(cid)

    def get_qr(self, data):
        return f'http://qrcoder.ru/code/?{data}&6&0'

    def register_activity(self, activity):
        cid = int(activity.get('cid'))
        dt = datetime.datetime.now(tz=self._tz)
        tid = int(activity.get('tid'))
        value = activity.get('value')
        self._db.register_activity(cid, dt, tid, value)

    def generate_confirmation_code(self, login):
        cid, name, scores, qr = self.get_info_by_login(login)
        token = self.get_token(cid)
        now = datetime.datetime.now(tz=self._tz)
        data = [cid, name, scores, token, now]
        code = self._generate_new_token(data)
        self._db.set_confirmation_code(cid, code)
        return code

    def clear_confirmation_code(self, cid):
        self._db.set_confirmation_code(cid, None)

    def get_confirmation_code(self, cid):
        return self._db.get_confirmation_code_by_cid(cid)

    def check_accruing_qr(self, content):
        result = self._db.check_accruing_qr(content)
        return result

    def check_deducting_qr(self, content):
        result = self._db.check_deducting_qr(content)
        return result

    def accrue_deduct(self, cid, value):
        self._db.accrue_deduct(cid, value)

    def send_code(self, email):
        smtpObj = smtplib.SMTP('smtp.mail.ru', 587)
        smtpObj.starttls()
        smtpObj.login('kirill_nikonenko@mail.ru', 'xB8QQ6cN9E')
        SUBJECT = "Confirmation Code"
        TO = email
        FROM = "OOO ChainShops <kirill_nikonenko@mail.ru>"
        code = self.generate_confirmation_code(email)
        text = f'Your confirmation code: {code}'
        BODY = "\r\n".join((
            "From: %s" % FROM,
            "To: %s" % TO,
            "Subject: %s" % SUBJECT,
            "",
            text
        ))
        smtpObj.sendmail(FROM, [TO], BODY)
        smtpObj.quit()

    def check_ip(self, ip):
        if len(self._db.check_ip(ip)) == 0:
            self._db.register_ip(ip)

    def check_order(self, ip, now_step, last_step):
        if last_step == 0 and now_step in (1, 2):
            return True
        elif last_step == 1 and now_step in (1, 4, 5, 6):
            return True
        elif last_step == 2 and now_step in (2, 3):
            self._db.update_try(ip)
            if self._db.get_try(ip) >= 3:
                self._db.to_block(ip)
                return False
            return True
        elif last_step == 3 and now_step in (3, 4, 5, 6):
            self._db.update_try(ip)
            if self._db.get_try(ip) >= 3:
                self._db.to_block(ip)
                return False
            return True
        elif last_step == 4 and now_step in (4, 5, 6):
            return True
        elif last_step == 5 and now_step in (1, 2):
            return True
        elif last_step == 6 and now_step in (4, 5, 6):
            return True
        else:
            return False

    def check_request(self, ip, now_cid, now_step):
        self.check_ip(ip)
        if not self._db.get_blocked(ip):
            if now_cid != self._db.get_cid_ip(ip):
                self._db.update_cid(ip, now_cid)
            if self.check_order(ip, now_step, self._db.get_step(ip)):
                if now_step != self._db.get_step(ip):
                    self._db.update_step(ip, now_step)
                return True
            else:
                self._db.update_step(ip, 0)
                return False
        else:
            return False
