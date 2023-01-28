''' query_string 解析 '''

import re
from urllib.parse import unquote
from app.sqlrest.util import symbol_split
from app.sqlrest.where import Where
from app.sqlrest.field import Field
from app.sqlrest.relation import Relation

class Query:
    def __init__(self, table, query_string):
        if not table:
            raise Exception("params error: table")
        self.table_name  = table
        self.table_query = unquote(query_string)
        self.group = []
        self.order = []
        self.limit = 0
        self.offset = 0
        self.meta = []
        self.page = 1   # 默认页
        self.size = 1000  # 默认数据数

        self.relation = []
        self.where = []
        self.fields = []
        self.keywords  = ['meta', 'field', 'group', 'size', 'page', 'sort']
        # 提取query_string信息
        self.parse()
    
    # 解析函数
    def parse(self):
        if not self.table_query:
            return
        for i in self.table_query.split("&"):
            key, val = i.split("=", 1)
            key = key.lower().strip()
            val = val.replace(" ", "")
            if not val: continue
            
            self.parse_page(key, val)
            self.parse_field(key, val)
            self.parse_order(key, val)
            self.parse_group(key, val)
            self.parse_where(key, val)
            self.parse_meta(key, val)
                
    def parse_where(self, key, value):
        if key in self.keywords:
            return 
        if value == "like.**":
            return 
        self.where.append(Where(key, value))
    
    def parse_meta(self, key, value):
        if key != "meta":
            return 
        self.meta = value.split(",")
    
    def parse_page(self, key, value):
        if key == "size":
            if value.isdigit(): 
                self.size = int(value)
        elif key == "page":
            if value.isdigit(): 
                self.page = int(value)
    
    # 解析 field
    def parse_field(self, key, value):
         # 解析field
        if key != "field":
            return 
        values = symbol_split(value)
        for field in values:
            rela_obj = Relation(field)
            if rela_obj.check_query():
                self.relation.append(rela_obj)
                self.fields.append(Field(rela_obj.master_key))
            else:
                self.fields.append(Field(field))
    
    # 解析 sort
    def parse_order(self, key, value):
        '''
        order=created_at,-weight
        '''
        if key != "sort":
            return 
        ls = [i.strip() for i in value.split(",") if i]
        for sort in ls:
            if sort.startswith("-"):
                sort = sort.replace("-", "")
                sort += " DESC"
            self.order.append(sort)
    
    # 解析 group
    def parse_group(self, key, val):
        if key != "group":
            return 
        self.group = [field for field in val.split(",") if field]
        return self.group
    
    # 更具field定义，做数据类型转化
    def data_convert(self, fields, data):
        # key 重命名，类型转化
        # 没有field 定义，直接转
        for item in data:
            for key, val in item.items():
                res = list(filter(lambda x: x.name == key, fields))
                if res:
                    field = res[0]
                else:
                    field = Field(key)
                item[key] = field.format_value(val)
        return data

    # 生成sql关键字
    def build_sql_node(self):
        node = {
            "table": "", "field": "", "where": "", "groupby": "", "orderby": "", "limit": "",
        }
        # table
        node['table'] = self.table_name.replace(".", "")
        # field
        
        if self.fields:
            fields = [i.to_sql() for i in self.fields]
            node['field'] = ",".join(fields)
        else:
            node['field'] = "*"
        # where 
        if self.where:
            where = [i.to_sql() for i in self.where]
            node['where'] = " WHERE " + " AND ".join(where)
        # group by
        if len(self.group) > 0:
            node['groupby'] = " GROUP BY " + ",".join(self.group)
        # order by
        if len(self.order) > 0:
            node['orderby'] = " ORDER BY " + ",".join(self.order)
        # limit 
        if self.page < 1:
            raise ValueError("page or size error!")
        self.limit = self.size
        self.offset = (int(self.page)-1) * int(self.size)
        node['limit'] = f" LIMIT {self.offset},{self.limit}"
        return node

     # sql
    def to_sql(self):
        n = self.build_sql_node()
        sql = f"SELECT {n['field']} FROM {n['table']} {n['where']} {n['groupby']} {n['orderby']} {n['limit']}"
        sql = re.sub(r"\s+", " ", sql)
        print("QUERY SQL>>>", sql)
        return sql
    
    # meta 函数 查询总数
    def to_count_sql(self):
        n = self.build_sql_node()
        sql = f"SELECT count(1) cnt FROM {n['table']} {n['where']} {n['groupby']}"
        sql = re.sub(r"\s+", " ", sql)
        print("COUNT SQL>>>", sql)
        return sql
      
    # 插入sql
    def to_insert_sql(self, data, replace=False):
        length, keys, insert_data = self.data2sqlvalue(data)
        if type(insert_data) is tuple:
            insert_data = [insert_data]
        data = [
            "(" + ",".join([f"'{i}'" if i is not None else 'NULL' 
            for i in d]) + ")" for d in insert_data
        ]
        sql = "INSERT INTO %s (%s) VALUES %s" % (self.table_name, ', '.join( [f"`{i}`" for i in keys]), ', '.join(data))
        if replace:
            sql += (' ON DUPLICATE KEY UPDATE ' + ', '.join(['%s=VALUES(%s)' % (x, x) for x in keys]))
        # sqlalcheme parse bug
        sql = sql.replace(":", "\:")
        print("INSERT SQL>>>", sql)
        return sql
    
    # 更新sql
    def to_update_sql(self, data):
        n = self.build_sql_node()
        sql = "UPDATE %s SET %s" % (
            self.table_name,
            ",".join([
                f"`{k}`='{v}'" if v is not None else f"`{k}`=NULL"
                for k, v in data.items()
            ]),
        )
        # where 
        sql += n['where']
        # sqlalcheme parse bug
        sql = sql.replace(":", "\:")
        print("UPDATE SQL>>>", sql)
        return sql

    # 删除sql
    def to_delete_sql(self):
        n = self.build_sql_node()
        sql = "DELETE FROM %s " % (self.table_name)
        sql += n['where']
        sql = sql.replace(':', '\:')
        print("DELETE SQL>>>", sql)
        return sql

    def data2sqlvalue(self, data):
        if isinstance(data, dict):
            item = data
            keys = item.keys()
            length = len(item)
            values = tuple([str(i) if i is not None else None for i in item.values()])
        elif isinstance(data, list):
            item = data[0]
            keys = item.keys()
            length = len(item)
            values = [
                tuple([str(i) if i is not None else None for i in item.values()])
                for item in data
            ]
        elif data is None:
            return None, None, None
        else:
            raise Exception("data type error")
        return length, keys, values
    