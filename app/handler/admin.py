from sanic import Blueprint
from app.handler.base import success, error, login_required
from app.config import setting

router = Blueprint("admin")

@router.route("/admin/tables")
async def get_tables(request):
    db = request.app.db
    database = setting['mysql']['db']
    list = await db.query(f"SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA='{database}'")
    tables = [i['TABLE_NAME'] for i in list]
    return success(tables)