'''
copy SanicDB...
'''

import traceback
import aiomysql
import pymysql


class Mysql:
    """A lightweight wrapper around aiomysql.Pool for easy to use
    """
    def __init__(self, host, port, database, user, password,
                 loop=None, sanic=None,
                 minsize=3, maxsize=5,
                 return_dict=True,
                 pool_recycle=7*3600,
                 autocommit=True,
                 charset = "utf8mb4", **kwargs):
        '''
        kwargs: all parameters that aiomysql.connect() accept.
        '''
        self.db_args = {
            'host': host,
            'port': port,
            'db': database,
            'user': user,
            'password': password,
            'minsize': minsize,
            'maxsize': maxsize,
            'charset': charset,
            'loop': loop,
            'autocommit': autocommit,
            'pool_recycle': pool_recycle,
        }
        self.sanic = sanic
        if sanic:
            sanic.db = self
        if return_dict:
            self.db_args['cursorclass']=aiomysql.cursors.DictCursor
        if kwargs:
            self.db_args.update(kwargs)
        self.pool = None

    async def init_pool(self):
        if self.sanic:
            self.db_args['loop'] = self.sanic.loop
        self.pool = await aiomysql.create_pool(**self.db_args)

    async def query(self, query, parse=False, *parameters, **kwparameters):
        """Returns a row list for the given query and parameters."""
        if not self.pool:
            await self.init_pool()
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                try:
                    if parse:
                        await cur.execute(query, kwparameters or parameters)
                    else:
                        await cur.execute(query)
                    ret = await cur.fetchall()
                except pymysql.err.InternalError:
                    await conn.ping()
                    await cur.execute(query)
                    ret = await cur.fetchall()
                return ret

    async def get(self, query, *parameters, **kwparameters):
        """Returns the (singular) row returned by the given query.
        """
        if not self.pool:
            await self.init_pool()
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                try:
                    await cur.execute(query, kwparameters or parameters)
                    ret = await cur.fetchone()
                except pymysql.err.InternalError:
                    await conn.ping()
                    await cur.execute(query, kwparameters or parameters)
                    ret = await cur.fetchone()
                return ret

    async def execute(self, query, *parameters, **kwparameters):
        """Executes the given query, returning the lastrowid from the query."""
        if not self.pool:
            await self.init_pool()
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                try:
                    await cur.execute(query, kwparameters or parameters)
                except Exception:
                    # https://github.com/aio-libs/aiomysql/issues/340
                    await conn.ping()
                    await cur.execute(query, kwparameters or parameters)
                return cur.lastrowid

    # high level interface
    # 创建表
    async def create_table(self, table):
        sql = f'''CREATE TABLE `{table}`( 
            `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
            `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (`id`)
        ) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4'''
        print(">>>", sql)
        res = await self.execute(sql)
        return res
    # 所有表
    async def tables(self, database):
        sql = f"SELECT table_name FROM information_schema.tables WHERE table_schema='{database}'"
        print(">>>", sql)
        tables = await self.query(sql)
        table_list = list(map(lambda x: x['table_name'], tables))
        return table_list
    
    # 表结构
    async def table_fields(self, name):
        sql = f"SELECT column_name name,data_type type,column_comment comment,column_default value FROM information_schema.columns WHERE table_name='{name}'"
        print(">>>", sql)
        table_info = await self.query(sql)
        return table_info

    # 添加字段
    async def add_field(self, table, field, type):
        sql = f"ALTER TABLE {table} ADD {field} {type}"
        print(">>>", sql)
        res = await self.execute(sql)
        return res
    
    async def drop_field(self, table, field):
        sql = f"ALTER TABLE {table} DROP {field}"
        print(">>>", sql)
        res = await self.execute(sql)
        return res