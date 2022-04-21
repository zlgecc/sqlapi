# coding: utf-8
import os
from sanic import Sanic
from sanic.log import *
from sanic import response
from sanic.exceptions import RequestTimeout, NotFound
import logging

from app.config import setting
from app.middleware import cors
from app.sqlrest.mysql import DB
from app.router import routes

# log init
app_config = setting['app']
log_path = app_config['log_path']
os.makedirs(log_path, exist_ok=True)
logging.basicConfig(filename=f'{log_path}/system.log', level=logging.DEBUG)


# server init
def server_init():
    app = Sanic(app_config['name'], configure_logging=LOGGING_CONFIG_DEFAULTS)

    db_config = setting['mysql']
    db = DB(host=db_config['host'], 
            port=int(db_config['port']), 
            database=db_config['db'], 
            user=db_config['user'], 
            password=db_config['password'], 
            sanic=app)
        
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


if __name__ == "__main__": 
    app = server_init()
    # Register blueprint
    app.blueprint(routes)
    app.run(host="0.0.0.0", port=app_config['port'], debug=app_config['debug'])
