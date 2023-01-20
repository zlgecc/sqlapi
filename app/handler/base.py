# coding: utf-8
import httpx
from sanic.log import logger
from sanic.response import json as respoonse_json
import json
import asyncio
import time
from functools import wraps
from app import config
import hashlib
import jwt


TOKEN_SECRET = config.get("app.token_secret")


def response(code=0, msg="", data={}):
    return respoonse_json({"code": code, "msg": msg, "data": data}, ensure_ascii=False)

def success(result, msg="success"):
    return response(code=0, msg=msg, data=result)

def error(msg="error", result={}):
    return response(code=500, msg=msg, data=result)



def encode_token(data):
    ts = time.time()
    data['ts'] = ts
    token = jwt.encode(data, TOKEN_SECRET, algorithm="HS256")
    return token
    
    
def hash_md5(string):
    m = hashlib.md5()
    m.update(string.encode('utf-8'))
    return m.hexdigest()


def check_token(token):
    if not token:
        return False
    try:
        curr_ts = time.time()
        info = jwt.decode(token, TOKEN_SECRET, algorithms=["HS256"])
        ts = info.get('ts', 0)
        if curr_ts - ts > 60*60*24*7:
            return False
    except jwt.exceptions.InvalidTokenError:
        return False
    else:
        return True
    

# token校验装饰器
def login_required(wrapped):
    def decorator(f):
        @wraps(f)
        async def decorated_function(request, *args, **kwargs):
            token = request.headers.get('token')
            is_authenticated = check_token(token)
            open_auth = config.get('app.open_auth')
            if open_auth and not is_authenticated:
                return response(code=401, msg="token无效或过期")
            
            resp = await f(request, *args, **kwargs)
            return resp
        return decorated_function
    return decorator(wrapped)

# http
async def http_client(url, data=None, timeout=30, method="GET", **kwargs):
    async with httpx.AsyncClient(verify=False) as client:
        logger.debug(f"posting url: {url}; data: {data}")
        if isinstance(data, dict):
            data = json.dumps(data)
        res = await client.request(method=method, url=url, data=data, timeout=timeout, **kwargs)
        print(res)
        print(res.content)
        res = res.json()
        return res

# 运行脚本
async def run_shell(cmd):
    proc = await asyncio.subprocess.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await proc.communicate()
    logger.debug('cmd: {}, returncode: {}'.format(cmd, proc.returncode))
    if stdout:
        stdout = str(stdout, encoding = "utf-8")
        logger.debug("\033[1;{};1m{}\033[0m".format(32, stdout))
    if stderr:
        stderr = str(stderr, encoding = "utf-8")
        logger.debug("\033[1;{};1m{}\033[0m".format(31, stderr))
    succ = False if proc.returncode != 0 else True
    return succ, stderr
