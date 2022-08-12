import json
import logging
import sys
# logging.basicConfig(level=logging.DEBUG)

def set_logger(logger: logging.Logger, path: str, is_json: bool = False):
    handler = logging.FileHandler(path)
    log_format = {}
    if logger.name == "sanic.access":
        log_format['request'] = "%(request)s"
        log_format['status'] = "%(status)s"
        log_format['byte'] = "%(byte)s"
    log_format["time"] = "%(asctime)s"
    log_format["name"] = "%(name)s"
    log_format["levelname"] = "%(levelname)s"
    log_format["levelno"] = "%(lineno)d"
    log_format["message"] = "%(message)s"
    
    if is_json:
        format = json.dumps(log_format)
    else:
        format = " - ".join(log_format.values())
    formatter = logging.Formatter(format)

    # 所有格式设置json
    for log_handler in logger.handlers:
        log_handler.setFormatter(formatter)
        
    handler.setFormatter(formatter)
    logger.addHandler(handler)
