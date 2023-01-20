from app.dbcli.mysql import Mysql
from app.dbcli.sqlite import Sqlite


class Database():

    def __init__(self, host, port, user, password, database, sanic, type="mysql"):
        self.db_conf = {
            'host': host,
            'port': port,
            'user': user,
            'password': password,
            'database': database,
        }
        self.type = type
        self.sanic = sanic
        return None
    
    def instance(self):
        if self.type == "mysql":
           return Mysql(sanic=self.sanic, **self.db_conf)
        if self.type == "sqlite":
            return Sqlite(sanic=self.sanic)
        return None
        