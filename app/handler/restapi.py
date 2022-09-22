# coding: utf-8
import traceback
from sanic import Blueprint
from app.sqlrest.api import QuerySQL, InsertSQL, UpdateSQL, DeleteSQL
from app.handler.base import success, error, login_required
from app.config import setting

router = Blueprint("api")

@router.route("/api/tables")
async def get_tables(request):
    db = request.app.db
    database = setting['mysql']['db']
    table_list = await db.query(f"SELECT table_name FROM information_schema.tables WHERE table_schema='{database}'")
    tables = {}
    for i in table_list:
        table = i['table_name']
        table_info = await db.query(f"SELECT column_name name ,data_type type,column_comment comment  FROM information_schema.columns WHERE table_name='{table}'")
        tables[table] = table_info
    return success(tables)


# select data
@router.route("/api/<table>", methods=["GET"])
@login_required
async def get(request, table):
    # 获取 uri
    query = request.query_string
    obj = QuerySQL(table, query)
    result = {}
    try:
        result = await obj.run(db=request.app.db)
    except Exception as e:
        traceback.print_exc()
        return error(f"Invalid param: {str(e)}")

    return success(result)

# create data
@router.route("/api/<table>", methods=["POST"])
@login_required
async def post(request, table):
    query = request.query_string
    data = request.json
    # 有query触发更新
    if query:
        obj = UpdateSQL(table, query, data)
    else:
        obj = InsertSQL(table, data)
    result = await obj.run(db=request.app.db)
    return success(result)

# update data
@router.route("/api/<table>", methods=["PUT"])
@login_required
async def put(request, table):
    query = request.query_string
    data = request.json
    obj = UpdateSQL(table, query, data)
    result = await obj.run(db=request.app.db)
    return success(result)

# delete data
@router.route("/api/<table>", methods=["DELETE"])
@login_required
async def delete(request, table):
    query = request.query_string
    obj = DeleteSQL(table, query)
    result = await obj.run(db=request.app.db)
    return success(result)