# coding: utf-8
from sanic import Blueprint
from sanic.log import logger
from app.handler.base import success, error
from app import config, token
import time
router = Blueprint("user")

@router.route("/auth", methods=['POST'])
async def auth(request):
    data = request.json
    ak = data.get('ak')
    sk = data.get('sk')
    if not all([ak, sk]):
        raise ValueError("请输入ak或者sk")
    
    print(ak, sk)
    timestamp = int(time.time())
    # 判断配置用户
    if ak == config.get("admin.user") and sk == config.get("admin.password"):
        jwt_token = token.encode_jwt({'username': ak, 'timestamp': timestamp})
        return success({"username": "admin", "token": jwt_token}, 'success')
    # 判断库中用户
    pw = token.md5(sk)
    sql = f'''SELECT * FROM user WHERE name="{sk}" AND password_hash="{pw}" '''
    userinfo = await request.app.db.get(sql)
    if not userinfo:
        raise ValueError("认证失败")
    # create token
    jwt_token = token.encode_jwt({'username': ak, 'timestamp': timestamp})
    return success({"token": jwt_token})
    
