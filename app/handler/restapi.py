# coding: utf-8
import traceback
from sanic import Blueprint
from app.sqlrest.api import QuerySQL, InsertSQL, UpdateSQL, DeleteSQL
from app.handler.base import success, error, login_required

router = Blueprint("api")

# select data
@router.route("/api/<table>", methods=["GET"])
# @login_required
async def get(request, table):
    # 获取 uri
    query = request.query_string
    obj = QuerySQL(table, query)
    data = []
    try:
        data = await obj.run(db=request.app.db)
    except Exception as e:
        traceback.print_exc()
        return error(f"Invalid param: {str(e)}")

    return success({"list": data})

# create data
@router.route("/api/<table>", methods=["POST"])
# @login_required
async def post(request, table):
    data = request.json
    obj = InsertSQL(table, data)
    result = await obj.run(db=request.app.db)
    return success(result)

# update data
@router.route("/api/<table>", methods=["PUT"])
# @login_required
async def put(request, table):
    query = request.query_string
    data = request.json
    obj = UpdateSQL(table, query, data)
    result = await obj.run(db=request.app.db)
    return success(result)

# delete data
@router.route("/api/<table>", methods=["DELETE"])
# @login_required
async def delete(request, table):
    query = request.query_string
    obj = DeleteSQL(table, query)
    result = await obj.run(db=request.app.db)
    return success(result)