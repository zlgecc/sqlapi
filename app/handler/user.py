# coding: utf-8
import traceback
from sanic import Blueprint
from sanic.log import logger
from app.handler.base import success, error, hash_md5, encode_token
from app import config
import time

router = Blueprint("user")

@router.route("/v1/auth", methods=['POST'])
async def auth(request):
    data = request.json
    try:
        username = data['username']
        password = data['password']
    except Exception as e:
        traceback.print_exc()
        raise ValueError("username或者password错误")
    
    timestamp = int(time.time())
    print(username, password)
    if username == config.get("admin.username") and password == config.get("admin.password"):
        print('login admin')
        return success({"username": "admin"}, 'success')
    else:
        pw = hash_md5(password)
        sql = f'''SELECT id,name,realname,email,phone FROM user WHERE name="{username}" AND password_hash="{pw}" '''
        userinfo = await request.app.db.get(sql)
        if not userinfo:
            raise ValueError("username或者password错误")
        
    # create token
    token = encode_token({'username': username, 'timestamp': timestamp})
    return success({"token": token})
    
