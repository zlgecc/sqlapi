
from app import config
import time
import jwt
import hashlib

TOKEN_SECRET = config.get("app.token_secret")

# 数据token
def encode_jwt(data):
    data['ts'] =  int(time.time())
    token = jwt.encode(data, TOKEN_SECRET, algorithm="HS256")
    return token

# 验证token
def check_jwt(token, expire=3600*7*24):
    if not token:
        return False
    try:
        curr_ts = time.time()
        info = jwt.decode(token, TOKEN_SECRET, algorithms=["HS256"])
        ts = info.get('ts', 0)
        if curr_ts - ts > expire:
            return False
    except jwt.exceptions.InvalidTokenError:
        return False
    else:
        return True

# md5
def md5(string):
    m = hashlib.md5()
    m.update(string.encode('utf-8'))
    return m.hexdigest()