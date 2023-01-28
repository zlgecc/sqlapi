# coding: utf-8
import httpx
from sanic.log import logger
from sanic.response import json as respoonse_json
import json
import asyncio
from functools import wraps
from app import config, token


def response(code=0, msg="", data={}):
    return respoonse_json({"code": code, "msg": msg, "data": data}, ensure_ascii=False)

def success(result, msg="success"):
    return response(code=0, msg=msg, data=result)

def error(msg="error", result={}):
    return response(code=500, msg=msg, data=result)

# token校验装饰器
def login_required(wrapped):
    def decorator(f):
        @wraps(f)
        async def decorated_function(request, *args, **kwargs):
            token_str = request.headers.get('token')
            is_authenticated = token.check_jwt(token_str)
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
