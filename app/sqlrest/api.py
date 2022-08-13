# coding: utf-8
import os, sys
osp = os.path
path = osp.dirname(osp.dirname(osp.abspath(__file__)))
sys.path.append(path)

import re
from urllib.parse import unquote
from app.sqlrest.variables.relation import Relation
from app.sqlrest.variables.select import Select
from app.sqlrest.variables.where import Where
from app.sqlrest.util import symbol_split
from enum import Enum
class Base:
    def to_sql(self):
        return ""

    def run(self):
        return {}

# Generate SQL
class QuerySQL(Base):
    def __init__(self, table, query):
        if not table:
            raise Exception("params error: table")
        self.table_name  = table
        self.table_query = unquote(query)
        self.group       = []
        self.order       = []
        self.limit       = 0
        self.offset      = 0
        self.meta        = []
        self.page        = 1   # 默认页
        self.size        = 1000  # 默认数据数

        self.relation = []
        self.where    = Where(self.table_name)
        self.select   = Select(["*"], self.table_name)
        self.urlkeys  = ['meta', 'field', 'group', 'size', 'page', 'sort']
        self.parse()

    # start 
    async def run(self, db):
        result = {"list": []}
        sql = self.to_sql()
        print(">>> query to sql:\n", sql)

        data_list = await db.query(query=sql)
        # data_list = [dict(i) for i in rows]
        
        # 加速批量查询
        rela_ids = {}
        rela_data = {}
        for index, val in enumerate(data_list):
            item = self.select.parse_field_data(val)
            for relation in self.relation:
                key_group_id = f'{relation.table}_ids'
                group_ids = val[key_group_id]
                if not group_ids :
                    group_ids = ''
                ids = set(group_ids.split(','))
                item[key_group_id] = group_ids.split(',')
                if relation.table in rela_ids.keys():
                    rela_ids[relation.table] |= ids
                else:
                    rela_ids[relation.table] = ids
            data_list[index] = item

        
        for rela_table, ids in rela_ids.items():
            fields = None
            relation = None 
            for rela in self.relation:
                if rela_table == rela.table:
                    fields = rela.sql_fields()
                    relation = rela
            ids = list(filter(lambda x: x, ids))
            table_data = []
            if len(ids) > 0:
                where = ','.join(ids)
                sql = f'SELECT {fields} FROM {rela_table} WHERE id in ({where})'
                print('>>> join sql:\n', sql)
                query_data = await db.query(query=sql)
                table_data = [relation.select.parse_field_data(dict(i)) for i in query_data]
            rela_data[rela_table] = table_data

        for index, val in enumerate(data_list):
            for relation in self.relation:
                key_group_id = f'{relation.table}_ids'
                group_ids = val[key_group_id]
                rdata = list(filter(lambda x: str(x['id']) in group_ids, rela_data[relation.table]))
                if relation.type == '1v1':
                    rdata = rdata[0] if len(rdata) > 0 else {}
                val[relation.table] = rdata
                del val[key_group_id]
            data_list[index] = val
        
        result['list'] = data_list
        
        # meta 函数``
        if "total" in self.meta:
            count_sql = self.to_count_sql()
            print('>>> count_sql:\n', count_sql)
            count = await db.query(count_sql)
            result["meta"] = {"total": count[0]['cnt']}
        
        return result
  
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
            self.parse_select(key, val)
            self.parse_order(key, val)
            self.parse_group(key, val)
            self.parse_where(key, val)
            self.parse_meta(key, val)
                
    def parse_where(self, key, value):
        if key in self.urlkeys:
            return 
        self.where.parse(key, value)
    
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
    def parse_select(self, key, value):
         # 解析field
        if key != "field":
            return 
        values = symbol_split(value)
        fields = []
        for field in values:
            if Relation.is_relation(field):
                rela_obj = Relation(field, self.table_name)
                self.relation.append(rela_obj)
            else:
                fields.append(field)

        field_obj = Select(fields, self.table_name)
        self.select = field_obj
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
            sort = self.table_field(sort)
            self.order.append(sort)
    # 解析 group
    def parse_group(self, key, val):
        if key != "group":
            return 
        self.group = [self.table_field(field) for field in val.split(",") if field]
        return self.group

    def table_field(self, field):
        if field.find(".") < 0:
            return f"{self.table_name}.{field}"
        return field
    # sql
    def to_sql(self):
        field, table, join, where, groupby, orderby, limit = self.generate_sql_segment()
        sql = f"SELECT {field} FROM {table} {join} {where} {groupby} {orderby} {limit}"
        sql = re.sub(r"\s+", " ", sql)
        return sql
    
    # meta 函数 查询总数
    def to_count_sql(self):
        field, table, join, where, groupby, orderby, limit = self.generate_sql_segment()
        sql = f"SELECT count(1) cnt FROM {table} {join} {where} {groupby} {orderby}"
        sql = re.sub(r"\s+", " ", sql)
        return sql
      
    # 生成sql关键字
    def generate_sql_segment(self):
        field, table, join, where, groupby, orderby, limit = 7 * [""]
        # table
        table = self.table_name.replace(".", "")

        fields = []

        if len(self.relation):
            # group master table
            group_id = self.table_field("id")
            if group_id not in self.group:
                self.group.insert(0, group_id)
                
        for relation in self.relation:
            join_info = relation.sql_join()
            join += join_info
            relation_table = relation.table
            func_field = f"GROUP_CONCAT({relation_table}.id) {relation_table}_ids"
            fields.append(func_field)
            
        # field
        fields.append(self.select.to_select_sql())
        field = ",".join(fields)
        
        # where 
        if self.where.to_sql():
            where = " WHERE " + self.where.to_sql()
        # group by
        if len(self.group) > 0:
            groupby = " GROUP BY " + ",".join(self.group)
        # order by
        if len(self.order) > 0:
            orderby = " ORDER BY " + ",".join(self.order)
        # limit 
        if self.page < 1:
            raise ValueError("page or size error!")
        self.limit = self.size
        self.offset = (int(self.page)-1) * int(self.size)
        limit = f" LIMIT {self.offset},{self.limit}"

        return field, table, join, where, groupby, orderby, limit

    

class InsertSQL(Base):
    def __init__(self, table, data):
        if not table:
            raise Exception("params error: table")
        self.table_name = table
        self.data = data

    async def run(self, db):
        sql = self.to_sql()
        res = await db.execute(sql)
        return res
    
    def to_sql(self, replace=False):
        length, keys, insert_data = self.data2sqlvalue(self.data)
        if type(insert_data) is tuple:
            insert_data = [insert_data]
        data = [
            "(" + ",".join([f"'{i}'" if i is not None else 'NULL'
                            for i in d]) + ")" for d in insert_data
        ]
        sql = "INSERT INTO %s (%s) VALUES %s" % (self.table_name, ', '.join(
            [f"`{i}`" for i in keys]), ', '.join(data))
        if replace:
            sql += (' ON DUPLICATE KEY UPDATE ' +
                    ', '.join(['%s=VALUES(%s)' % (x, x) for x in keys]))
        # sqlalcheme parse bug
        sql = sql.replace(":", "\:")
        return sql

    def data2sqlvalue(self, data):
        if isinstance(data, dict):
            item = data
            keys = item.keys()
            length = len(item)
            values = tuple(
                [str(i) if i is not None else None for i in item.values()])
        elif isinstance(data, list):
            item = data[0]
            keys = item.keys()
            length = len(item)
            values = [
                tuple(
                    [str(i) if i is not None else None for i in item.values()])
                for item in data
            ]
        elif data is None:
            return None, None, None
        else:
            raise Exception("data type error")
        return length, keys, values

class UpdateSQL(QuerySQL):
    def __init__(self, table, query, data):
        super().__init__(table, query)
        self.data = data

    async def run(self, db):
        sql = self.to_sql()
        res = await db.execute(sql)
        return res
    
    def to_sql(self):
        sql = "UPDATE %s SET %s" % (
            self.table_name,
            ",".join([
                f"`{k}`='{v}'" if v is not None else f"`{k}`=NULL"
                for k, v in self.data.items()
            ]),
        )
        # where 
        if self.where.to_sql():
            where = " WHERE " + self.where.to_sql()
            sql += where
        # sqlalcheme parse bug
        sql = sql.replace(":", "\:")
        return sql

class DeleteSQL(QuerySQL):
    def __init__(self, table, query):
        super().__init__(table, query)
    
    async def run(self, db):
        sql = self.to_sql()
        res = await db.execute(sql)
        return res
    
    def to_sql(self):
        sql = "DELETE FROM %s " % (self.table_name)
        if self.where.to_sql():
            where = " WHERE " + self.where.to_sql()
            sql += where
        sql = sql.replace(':', '\:')
        return sql
