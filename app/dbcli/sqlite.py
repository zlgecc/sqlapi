''' sqliteclient easy to use '''

import aiosqlite


class Sqlite: 

    def __init__(self, sanic, database="sqlite.db"):
        self.sanic = sanic
        self.database = database
        self.conn = None
    
    async def connect(self):
        # self.conn = await aiosqlite.connect(self.database)
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

    # high level interface
    # 创建表
    async def create_table(self, table):
        sql = f'''CREATE TABLE `{table}`( 
            `id` integer PRIMARY KEY autoincrement,
            `created_at` datetime DEFAULT CURRENT_TIMESTAMP
        ) '''
        print(">>>", sql)
        res = await self.execute(sql)
        return res
    # 所有表
    async def tables(self, database):
        sql = f"SELECT name FROM sqlite_master WHERE type='table'"
        print(">>>", sql)
        tables = await self.query(sql)
        table_list = list(map(lambda x: x['name'], tables))
        return table_list
    
    # 表结构
    async def table_fields(self, name):
        sql = f"PRAGMA table_info({name})"
        print(">>>", sql)
        table_info = await self.query(sql)
        return table_info

    # 添加字段
    async def add_field(self, table, field, type):
        sql = f"ALTER TABLE {table} ADD COLUMN {field} {type}"
        print(">>>", sql)
        await self.execute(sql)
        return
    
    async def drop_field(self, table, field):
        sql = f"ALTER TABLE {table} DROP COLUMN {field}"
        print(">>>", sql)
        await self.execute(sql)
        return