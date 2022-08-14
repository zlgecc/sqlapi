# coding: utf-8

import os
import yaml

def get_env(key, default=""): 
    val = os.getenv(key)
    return val if val else default

config_path = f'./setting.yaml'
with open(config_path, 'r') as conf_file:
    setting = yaml.safe_load(conf_file)


def print_env(): 
    with open(config_path, 'r') as file:
        print(file.read())

def update_config(conf):
    setting.update(conf)
    return setting

# App config from the environment
appconf = setting['app']
appconf['debug']    = get_env("APP_DEBUG", appconf['debug'])
appconf['log_path'] = get_env("LOG_PATH", appconf['log_path'])

# db config from the environment
dbconf = setting['mysql']
mysql_conf = {"mysql": {
    "host": get_env('DB_HOST', dbconf['host']),
    "port": get_env('DB_PORT', dbconf['port']),
    'db': get_env('DB_NAME', dbconf['db']),
    'user': get_env('DB_USER', dbconf['user']),
    'password': get_env('DB_PASSWORD', dbconf['password'])
}}
update_config(mysql_conf)


