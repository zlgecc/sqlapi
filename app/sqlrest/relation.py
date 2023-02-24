from itertools import groupby
from app.sqlrest.util import cutout
from app.sqlrest.field import Field
import re


class Relation:
    ''' 连表信息 
        jobs[project_id=id, name,created_at]
    '''
    def __init__(self, query):
        self.query = query
        if not self.check_query():
            return
        self.table, field_match = cutout(r"[\[\{].*?[\]\}]", query)
        print(field_match)
        if field_match.startswith("["):
            self.type = 1
        elif field_match.startswith("{"):
            self.type = 0
        else: 
            raise ValueError("join格式错误")
        field_match = re.sub(r"[\[\]\{\}]", "", field_match)
        fields = field_match.split(",")
        if len(fields) < 1:
            raise ValueError("关联表缺少字段")
        if fields[0].find("=") == -1:
            # 默认关联条件
            master_key = f"{self.table}_id"
            relate_key = 'id'
            fields.insert(0, f"{master_key}={relate_key}")

        self.master_key, self.relate_key = fields[0].split("=")
        self.fields = [Field(i) for i in fields[1:]]
    
    def check_query(self):
        _, join_match = cutout(r"\w*[\[\{].*?[\]\}]", self.query)
        if join_match:
            return True
        return False

    def to_sql(self, where=""):
        self.fields.append(Field(self.relate_key))
        field = ",".join([i.to_sql() for i in self.fields])
        sql = f"SELECT {field} FROM {self.table} WHERE {where}"
        return sql

    def merge_table_data(self, data, relation_data):
        ''' 合并数据 '''
         # relation table key
        for i in data:
            i[self.table] = [] if self.type == 1 else {}
        for id, value in groupby(relation_data, lambda x: x[self.relate_key]):
            source_data = filter(lambda x: x[self.master_key]==id, data)
            relation_item = None
            if self.type == 1:
                relation_item = list(value)
            else:
                relation_item = list(value)[0]
            for item in source_data:
                item[self.table] = relation_item
            # print('---->', id, list(item))
        return data
