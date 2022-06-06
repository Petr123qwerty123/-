from Database.Database import Database


class ProductPosition:
    def __init__(self):
        self.gid = None
        self.title = None
        self.price = None
        self.quantity = 1
        self._db = Database()

    def set_good(self, gid):
        good_info = self._db.get_good_by_gid(gid)
        if len(good_info) != 0:
            self.gid = good_info[0][0]
            self.title = good_info[0][1]
            self.price = good_info[0][2]
            return True
        else:
            return False
