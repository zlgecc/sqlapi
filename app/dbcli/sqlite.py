''' sqliteclient easy to use '''

import aiosqlite


class Sqlite: 

    def __init__(self, sanic, database="sqlite.db"):
        self.sanic = sanic
        self.database = database
        self.conn = None
    
    async def connect(self):
        self.conn = await aiosqlite.connect(self.database, loop=self.sanic.loop)
        def dict_factory(cursor, row):
            d = {}
            for index, col in enumerate(cursor.description):
                d[col[0]] = row[index]
            return d
        self.conn.row_factory = dict_factory
        return self.conn


    async def query(self, query, *args, **kwargs):
        if not self.conn:
            await self.connect()
        async with self.conn.execute(query, *args, **kwargs) as cursor:
            ret = await cursor.fetchall()
            return ret

    async def get(self, query, *args, **kwargs):
        if not self.conn:
            await self.connect()
        async with self.conn.execute(query, *args, **kwargs) as cursor:
            ret = await cursor.fetchone()
            return ret

    async def execute(self, query, *args, **kwargs):
        if not self.conn:
            await self.connect()
        res = await self.conn.execute(query, *args, **kwargs)
        await self.conn.commit()

        return res


    async def table_insert(self, table_name, item):
        '''item is a dict : key is mysql table field'''
        if not self.conn:
            await self.connect()

        fields = list(item.keys())
        values = list(item.values())
        fieldstr = ','.join(fields)
        valstr = ','.join(['?'] * len(item))
        sql = 'INSERT INTO %s (%s) VALUES(%s)' % (table_name, fieldstr, valstr)
        print(sql)
        cursor = await self.conn.execute(sql, values)
        await self.conn.commit()
        return cursor.lastrowid

    async def table_update(self, table_name, updates, field_where, value_where):
        upsets = []
        values = []
        for k, v in updates.items():
            s = '%s=%%s' % k
            upsets.append(s)
            values.append(v)
        upsets = ','.join(upsets)
        sql = 'UPDATE %s SET %s WHERE %s="%s"' % (table_name, upsets, field_where, value_where)
        cursor = await self.conn.execute(sql, *(values))
        await self.conn.commit()
        return cursor.rowcount