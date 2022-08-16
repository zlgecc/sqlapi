# coding: utf-8
import os
from sanic import Sanic
from sanic.log import logger, access_logger, error_logger
from sanic import response
from sanic.exceptions import RequestTimeout, NotFound

from app.config import setting, update_config
from app.log import set_logger
from app.middleware import cors
from app.sqlrest.mysql import DB
from app.router import routes

import argparse

# log init
app_config = setting['app']
log_path = app_config['log_path']
os.makedirs(log_path, exist_ok=True)
logfile = log_path + "/app.log"
# logging.basicConfig(filename=f'{log_path}/system.log', level=logging.DEBUG)
set_logger(logger, logfile)
set_logger(access_logger, logfile)
set_logger(error_logger, logfile)

# server init
def server_init():
    app = Sanic(app_config['name'])

    db_config = setting['mysql']
    db = DB(host=db_config['host'], 
            port=int(db_config['port']), 
            database=db_config['db'], 
            user=db_config['user'], 
            password=db_config['password'], 
            sanic=app)

    # UI public
    if app_config["debug"]:
        app.static('/admin', './UI/dist/index.html')
        app.static('/assets', './UI/dist/assets/')

    # ping
    @app.route("/ping")
    def ping(request):
        return response.text('pong')

    # server event
    @app.listener("after_server_start")
    async def after_server_start(app, loop):
        await db.init_pool()

    # middleware
    @app.middleware("request")
    async def cros(request):
        if request.method == "OPTIONS":
            headers = cors.get_headers()
            return response.json({"code": 0}, headers=headers)


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
    dbconf = setting['mysql']
    for k, v in vars(args).items():
        if v: dbconf[k] = v
    update_config({"mysql": dbconf})
    if args.debug:
        app_config['debug'] = args.debug
        update_config({"app": app_config})


if __name__ == "__main__": 
    parse_args()
    app = server_init()
    # Register blueprint
    app.blueprint(routes)
    app.run(host="0.0.0.0", port=app_config['port'], debug=app_config['debug'])
