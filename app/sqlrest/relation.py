from itertools import groupby
from app.sqlrest.util import cutout
from app.sqlrest.field import Field
import re


class Relation:
    ''' 连表信息 
        jobs[$project_id=id, name,created_at]
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
        if len(fields) < 1 or fields[0].find("=") == -1:
            raise ValueError("缺少join条件或字段")

        self.master_key, self.relate_key = fields[0].split("=")
        self.fields = [Field(i) for i in fields[1:]]
    
    def check_query(self):
        _, join_match = cutout(r"\w*[\[\{].*?[\]\}]", self.query)
        if join_match:
            return True
        return False

    def to_sql(self):
        self.fields.append(Field(self.relate_key))
        field = ",".join([i.to_sql() for i in self.fields])
        sql = f"SELECT {field} FROM {self.table}"
        return sql

    def merge_table_data(self, data, relation_data):
        ''' 合并数据 '''
        for id, value in groupby(relation_data, lambda x: x[self.relate_key]):
            item = filter(lambda x: x[self.master_key]==id, data)
            relation_item = None
            if self.type == 1:
                relation_item = list(value)
            else:
                relation_item = list(value)[0]
            list(item)[0][self.table] = relation_item
            # print('---->', id, list(item))
        return data
