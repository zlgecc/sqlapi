# coding: utf-8

import os
import yaml

config_path = f'./config.yml'
with open(config_path, 'r') as conf_file:
    setting = yaml.safe_load(conf_file)


def get_env(key, default=""): 
    val = os.getenv(key)
    return val if val else default

def update_config(conf):
    setting.update(conf)
    return setting

def get(key="app.name"):
    """ 先去获取ENV，再去获取 config.yml
    例：app.name 先取 RA_APP_NAME 环境变量，再取 config.yml 的config['app']['name'] 
    """
    keys = key.split(".")
    env_key = f"RA_" + "_".join([i.upper() for i in keys])
    config_value = get_env(env_key)
    if not config_value:
        config_value = setting
        for k in keys:
            config_value = config_value.get(k)
    return config_value

def set(key, value):
    keys = key.split(".")
    config_value = setting
    for k in keys:
        config_value = config_value[k]
    config_value = value
    print(setting)


