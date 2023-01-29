# coding: utf-8
from sanic import Blueprint
from app.handler.base import success
from app import config

router = Blueprint("table")

# 创建表
@router.route("/table", methods=["POST"])
async def create_table(request):
    db = request.app.db
    table = request.args.get('name')
    res = await db.create_table(table)
    return success(res.lastrowid)

# 查所有表
@router.route("/table", methods=["GET"])
async def get_tables(request):
    db = request.app.db
    database = config.get("database.db")
    tables = await db.tables(database=database)
    return success(tables)

# 查表结构
@router.route("/table/field", methods=["GET"])
async def table_struct(request):
    db = request.app.db
    # 指定表
    table = request.args.get('name')
    if not table:
        raise ValueError("No table")
    table_info = await db.table_fields(name=table)
    return success(table_info)

# 添加字段
@router.route("/table/field", methods=["POST"])
async def add_field(request):
    db = request.app.db
    json = request.json
    table = json.get('table')
    field = json.get('field')
    type = json.get('type')
    if not all([table, field, type]):
        return ValueError('Invalid data')
    res = await db.add_field(table=table, field=field, type=type)
    return success(res)

# 删除字段
@router.route("/table/field", methods=["DELETE"])
async def del_field(request):
    db = request.app.db
    json = request.json
    table = json.get('table')
    field = json.get('field')
    if not all([table, field, type]):
        return ValueError('Invalid data')
    res = await db.drop_field(table=table, field=field)
    return success(res)
