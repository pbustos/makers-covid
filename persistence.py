from rethinkdb import RethinkDB
from rethinkdb.errors import RqlRuntimeError
import json
import time
import copy

class Persistence():
    def __init__(self):
        self.r = RethinkDB()
        self.conn = self.r.connect( "localhost", 28015)

    def insert(self, data):
        # add timestamp
        mydata = copy.deepcopy(data)
        mydata["time"] = int(time.time())
        self.last = mydata["time"]
        try:
            self.r.db('makers-covid').table('global').insert(mydata).run(self.conn)
        except RqlRuntimeError as err:
            print(err.message)
    
    def getLast(self):
        res = self.r.db('makers-covid').table('global').filter(self.r.row['time'] >= self.last).run(self.conn)
        return res.next()

