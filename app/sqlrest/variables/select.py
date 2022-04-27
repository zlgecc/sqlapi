# coding: utf-8
from datetime import datetime
import json
from sqlrest.util import cutout

class Select:
    infix = "__"

    def __init__(self, fields, base_table):
        self.base_table = base_table
        self.array      = []
        
        for field in fields:
            if field == "*" or field == '': 
                continue
            # 去掉函数
            field, _ = cutout(r'\(.*?\)', field)
            # 类型转换
            field, type_match = cutout(r'\|\w*', field)
            field_type = type_match.replace("|", "") if type_match else None
            # 别名
            field, alias_match = cutout(r':\w*', field)
            field_alias = alias_match.replace(":", "") if alias_match else None
            self.array.append(Field(name=field, table=base_table, alias=field_alias, conver=field_type))

    def __str__(self):
        print(self.array)
        return self.to_select_sql()
    
    # 转 sql
    def to_select_sql(self):
        fields = []
        for field in self.array:
            fields.append(field.table_field + ' ' + field.get_alias())
        sql = ",".join(fields)
        if sql == "":
            return str(Field("*", self.base_table))
        return sql


    def parse_field_data(self, data):
        fields = {}
        # 查所有 * 
        if len(self.array) == 0:
            for k, v in data.items():
                field = Field(k, self.base_table)
                data[k] = field.format_value(v)
            return data
        
        for field in self.array:
            value = data[field.get_alias()]
            value = field.format_value(value)
            key = field.get_alias(use_default=False)
            fields[key] = value
        return fields
    
    def remove_table_key(self, data):
        keys = list(data.keys()).copy()
        for k in keys:
            if k.startswith(self.base_table + self.infix):
                del data[k]
        return data


class Field:
    
    def __init__(self, name, table, alias=None, conver=None):
        self.infix         = "__"
        self.name          = name
        self.table         = table
        self.alias         = alias
        self.conver        = conver
        self.default_alias = self.table + self.infix + self.name
        self.table_field   = f"{self.table}.{self.name}"
        self.value         = None
        
    def __str__(self):
        return self.table_field
    def __repr__(self):
        return str(f'Field(table="{self.table}", name="{self.name}", value="{self.value}")')
    def __dict__(self):
        return {self.name: self.value}
    
    def get_alias(self, use_default=True):
        if self.alias:
            return self.alias
        return self.default_alias if use_default else self.name
    
    
    def format_value(self, value):
        if isinstance(value, datetime):
            value = value.strftime('%Y-%m-%d %H:%M:%S')
        conver = self.conver
        if conver == "int": 
            value = int(value)
        elif conver == "str": 
            value = str(value)
        elif conver == "json": 
            value = json.loads(value)
        elif conver == "float":
            value = float(value)
        self.value = value
        return value