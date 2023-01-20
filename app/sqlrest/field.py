# coding: utf-8
import datetime
import json
from app.sqlrest.util import cutout

class Field:
    ''' 查询字段 
        field=id,name,created_at:ca
    '''
    def __init__(self, query):
        self.query = query
        self.field_type = None
        self.alias = None
        # 去掉函数
        name, _ = cutout(r'\(.*?\)', self.query)
        # 类型转换
        name, type_match = cutout(r'\|\w*', name)
        self.field_type = type_match.replace("|", "") if type_match else None
        # 别名
        name, alias_match = cutout(r':\w*', name)
        self.alias = alias_match.replace(":", "") if alias_match else None
        self.name = name
    
    def get_key(self):
        return self.alias if self.alias else self.name

    def to_sql(self):
        return self.name + " " + self.alias if self.alias else self.name

    def format_value(self, value):
        if isinstance(value, datetime.datetime) or isinstance(value, datetime.date):
            value = value.strftime('%Y-%m-%d %H:%M:%S')
        conver = self.field_type
        if conver == "int": 
            value = int(value)
        elif conver == "str": 
            value = str(value)
        elif conver == "json": 
            value = json.loads(value)
        elif conver == "float":
            value = float(value)
        return value

    def __repr__(self):
        return str(f'Field(name="{self.name}", alias="{self.alias}")')