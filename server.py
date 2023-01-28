# coding: utf-8
import os
from sanic import Sanic
from sanic.log import logger, access_logger, error_logger
from sanic import response
from sanic.exceptions import RequestTimeout, NotFound

from app import config
from app.database import Database
from app.log import set_logger
from app.middleware import cors
from app.router import routes
from app import token

import argparse

# log init
log_path = config.get('app.log_path')
os.makedirs(log_path, exist_ok=True)
logfile = log_path + "/app.log"
# logging.basicConfig(filename=f'{log_path}/system.log', level=logging.DEBUG)
set_logger(logger, logfile)
set_logger(access_logger, logfile)
set_logger(error_logger, logfile)

# server init
def server_init():
    app = Sanic(config.get('app.name'))
    
    dbconf = dict(
        host=config.get('database.host'), 
        port=int(config.get('database.port')), 
        database=config.get('database.db'), 
        user=config.get('database.user'), 
        password=config.get('database.password'),
        type=config.get('database.type')
    )
    # db = DB(sanic=app, **dbconf)
    app.db = Database(sanic=app, **dbconf).instance()

    # UI public
    app.static('/admin', './UI/dist/index.html')
    app.static('/assets', './UI/dist/assets/')

    # ping
    @app.route("/ping")
    def ping(request):
        return response.text('pong')

    # server event
    @app.listener("after_server_start")
    async def after_server_start(app, loop):
        return 

    # middleware
    @app.middleware("request")
    async def before_request(request):
        if request.method == "OPTIONS":
            headers = cors.get_headers()
            return response.json({"code": 0}, headers=headers)
        
        # token 验证
        jwt_token = request.cookies.get('token')
        if not jwt_token:
            jwt_token = request.headers.get('token')
        is_authenticated = token.check_jwt(jwt_token)
        open_auth = config.get('app.open_auth')
        if request.path == '/auth':
            return 
        if open_auth and not is_authenticated:
            return response.json({"code": 401, "msg": 'token无效或过期'})


    @app.middleware("response")
    async def cors_res(request, response):
        if response is None:
            return response
        headers = cors.get_headers()
        response.headers.update(headers)
        return response

    # exception
    @app.exception(RequestTimeout)
    def timeout(request, exception):
        return response.json({"msg": "Request Timeout", "code": 408}, 408)


    @app.exception(NotFound)
    def notfound(request, exception):
        error_logger.warning("URI calledMy: {0} {1}".format(request.url, exception))
        return response.json({"msg": f"Requested URL {request.url} not found", "code": 404}, 404)


    @app.exception(Exception)
    def notfound(request, exception):
        error_logger.exception(exception)
        err = str(exception)
        return response.json({"msg": f"{err}", "code": 500}, status=500, ensure_ascii=False)
    
    return app

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", "-d", type=str)
    parser.add_argument("--user", "-u", type=str)
    parser.add_argument("--password", "-p", type=str)
    parser.add_argument("--host", "-H", type=str)
    parser.add_argument("--port", "-P", type=int)
    parser.add_argument("--debug", action="store_true", default=False)
    args = parser.parse_args()
    # update config
    for key, val in vars(args).items():
        if key in ['db', 'user', 'password', 'host', 'port'] and val:
            config.set(f'mysql.{key}', val)
        if key in ['debug'] and val:
            config.set(f'app.{key}', val)
  


if __name__ == "__main__": 
    parse_args()
    app = server_init()
    # Register blueprint
    app.blueprint(routes)
    app.run(host="0.0.0.0", port=config.get('app.port'), debug=config.get('app.debug'))
