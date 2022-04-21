# coding: utf-8

import os
import importlib

def find_routers(path, instance):
    routers = []
    # 动态导入
    handlers = os.listdir(path)
    for file in handlers:
        dirs = path.split('/')
        file = file.split('.')[0]
        dirs.append(file)

        pkg_path = ".".join(dirs)
        package = importlib.import_module(pkg_path)
        if hasattr(package, instance):
            print('import:', pkg_path, instance)
            routers.append(getattr(package, instance))
    return routers
        
routes = find_routers(path='app/handler', instance='router')
