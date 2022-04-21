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
        self.parse()

    # start 
    async def run(self, db):
        result = {"list": []}
        sql = self.to_sql()
        print("=================== sql =====================")
        print(sql)

        rows = await db.query(sql)
        list = [dict(i) for i in rows]
        # 输出格式化
        fmt_data = self.format_data(list)
        # meta 函数
        if "total" in self.meta:
            count_sql = self.to_count_sql()
            count = await db.get(count_sql)
            result["meta"] = {"total": count[0]}
        
        return fmt_data
    
    def data_key_conversion(self, item, fields, new=False):
        data = {}
        for field in fields:
            code_key = field.get_alias()
            result_key = field.get_alias(use_default=False)
            item[result_key] = item[code_key]
            data[result_key] = item[code_key]
            del item[code_key]
        if new:
            item = data
        return item
    
    
    
    # 数据转换，聚合
    def format_data(self, data):
        from functools import reduce
        # 格式规范
        process_data = []
        mtd_cache = None
        for item in data:
            tmp = self.select.parse_field_data(item)
            if tmp == mtd_cache:
                continue
            mtd_cache = tmp
            mtd = mtd_cache.copy()
            for relation in self.relation:
                if relation.type == '1vn':
                    def duplicate(x, y):
                        if not isinstance(x, list):
                            x = relation.select.parse_field_data(x)
                            x = [x]
                        y = relation.select.parse_field_data(y)
                        if y in x :
                            return x
                        else:
                            return x + [y]
                    # 去重
                    duplicate_data = reduce(duplicate, data)
                    # join过滤
                    master_key = relation.master_field.get_alias(use_default=False)
                    relate_key = relation.relate_field.get_alias(use_default=False)
                    condi = lambda x:mtd[master_key]==x[relate_key]
                    rtd = filter(condi, duplicate_data)
                    mtd[relation.table] = list(rtd)
                else:
                    # 一对一
                    mtd[relation.table] = relation.select.parse_field_data(item)
            process_data.append(mtd)
        return process_data
   
  
    # 解析函数
    def parse(self):
        if not self.table_query:
            return
        for i in self.table_query.split("&"):
            key, val = i.split("=", 1)
            key = key.lower().strip()
            val = val.replace(" ", "")
            if not val: continue
            if key == "size":
                if val.isdigit(): self.size = int(val)
            elif key == "page":
                if val.isdigit(): self.page = int(val)
            elif key == "sort":
                self.parse_order(val)
            elif key == "field":
                self.parse_select(val)
            elif key == "group":
                self.parse_group(val)
            elif key == "meta":
                self.meta = val.split(",")
            else:
                self.where.parse(key, val)
        
    # 生成sql关键字
    def generate_sql_segment(self):
        field, table, join, where, groupby, orderby, limit = 7 * [""]
        # table
        table = self.table_name.replace(".", "")

        fields = []
        # join relation
        if len(self.relation):
            for relation in self.relation:
                join_info, join_field = relation.to_variable()
                join += join_info
                # + join field
                fields.append(join_field)
        
        # field
        fields.append(self.select.to_select_sql())
        field = ",".join(fields)
        
        # where 
        if self.where.to_variable():
            where = " WHERE " + self.where.to_variable()
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

    # 解析 field
    def parse_select(self, value):
         # 解析field
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
        return
    
    # 解析 sort
    def parse_order(self, value):
        '''
        order=created_at,-weight
        '''
        ls = [i.strip() for i in value.split(",") if i]
        for sort in ls:
            if sort.startswith("-"):
                sort = sort.replace("-", "")
                sort += " DESC"
            sort = self.table_field(sort)
            self.order.append(sort)
    
    # 解析group
    def parse_group(self, val):
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
        if self.where.to_variable():
            where = " WHERE " + self.where.to_variable()
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
        if self.where.to_variable():
            where = " WHERE " + self.where.to_variable()
            sql += where
        sql = sql.replace(':', '\:')
        return sql
