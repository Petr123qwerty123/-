import datetime

from Database.Database import Database


class Cheque:
    def __init__(self):
        self._db = Database()
        self._offset = datetime.timedelta(hours=3)
        self._tz = datetime.timezone(self._offset, name='МСК')
        self.cheque_id = None
        self.cid = None
        self.scores = 0
        self.goods = {}

    def new_cheque(self):
        self.cheque_id = self._db.new_cheque()
        self.cid = None
        self.scores = 0
        self.goods = {}

    def edit_cheque(self, gid=None, cid=None, scores=None):
        if gid is not None:
            if self.goods.get(gid) is not None:
                self.goods[gid] += 1
            else:
                self.goods[gid] = 1
        if cid is not None:
            self.cid = cid
        if scores is not None:
            self.scores = scores

    def save_cheque(self):
        self._db.save_cheque(self)


