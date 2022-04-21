
import asyncio
from mysql import DB
from api import QuerySQL
from pprint import pprint

loop = asyncio.get_event_loop()
dbconf = {
    'host': 'mysql',
    'port': 3306,
    'user': 'root',
    'pw'  : "Aa_123456",
    'db'  : 'test_db',
}

db = DB(host=dbconf['host'], port=dbconf['port'], user=dbconf['user'], password=dbconf['pw'], database=dbconf['db'], loop=loop)

async def testdb():
    data = await db.query("SELECT * FROM user LIMIT 1")
    print(data)

async def testQuerySQL():
    # query = QuerySQL('user', "field=id,name,car[id,brand]")
    # query = QuerySQL('car', "field=id,name,user{id,name}")
    # query = QuerySQL('user', "field=id,name,car[id,name],driving_license[id,name]")
    query = QuerySQL('car', "field=id,name,user{id,name}")
    query = QuerySQL('car', "field=id:iii,name,user{id,name}")
    
    res = await query.run(db)
    pprint(res)

if __name__ == '__main__':
    ...
    # loop.run_until_complete(testdb())
    loop.run_until_complete(testQuerySQL())