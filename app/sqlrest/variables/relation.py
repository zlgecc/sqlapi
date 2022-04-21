# coding: utf-8 
import os, sys
osp = os.path
path = osp.dirname(osp.dirname(osp.dirname(osp.abspath(__file__))))
sys.path.append(path)

from sqlrest.util import cutout
import re
from app.sqlrest.variables.select import Select, Field
from itertools import groupby

# parse to_variable format_output

class Relation:

    def __init__(self, query, base_table):
        self.master_table = base_table

        if not self.is_relation(query):
            return
        self.table, field_match = cutout(r"[\[\{].*?[\]\}]", query)

        # 识别连表类型
        if field_match.startswith("["):
            self.type = "1vn"
            # default join on
            self.master_field = Field('id', self.master_table)
            self.relate_field = Field(f"{self.master_table}_id", self.table)
        elif field_match.startswith("{"):
            self.type = "1v1"
            # default join on
            self.master_field = Field(f'{self.table}_id', self.master_table)
            self.relate_field = Field(f"id", self.table)
        else:
            raise SyntaxError("Invalid join param")
        field_match = re.sub(r"[\[\]\{\}]", "", field_match)
        
        fields = field_match.split(",")
        if "*" in fields:
            raise ValueError("relation table not support *")

        
        # 识别指定 join on
        join_on = self.create_join_on(self.master_field, self.relate_field)
        if len(fields) > 0 and fields[0].find("=") != -1:
            master_key, relate_key = fields[0].split("=")
            self.master_field = Field(master_key, self.master_table)
            self.relate_field = Field(relate_key, self.table)
            join_on = self.create_join_on(self.master_field, self.relate_field)
            # 删除join指令
            fields.pop(0)
        
        self.join_on = join_on
        self.select  = Select(fields, self.table)
        
        
    def create_join_on(self, master, relate):
        return master.table_field + '=' + relate.table_field


    def to_variable(self):
        join_table = self.table
        relation_table = f" INNER JOIN {join_table} ON {self.join_on}"

        # 必须包含关键key字段
        self.select.array.append(self.relate_field)
        join_select_field = self.select.to_select_sql()
        return relation_table, join_select_field

    
    @classmethod
    def is_relation(cls, query):
        _, join_match = cutout(r"\w*[\[\{].*?[\]\}]", query)
        if join_match:
            return True
        return False


if __name__ == "__main__":
    # ls = ['id:iid', 'name|json', 'nickname']
    # fieldObj = Select(ls, 'user')
    # print(fieldObj.to_valiable())
    # print(str(fieldObj))

    print('================================')
    relaObj = Relation("camera{id,channel:c,device}", 'record')
    relation_table, join_field = relaObj.to_variable()
    print(relation_table)
    print(join_field)
    
    print(relaObj.generate_1vn_sql([1]))
