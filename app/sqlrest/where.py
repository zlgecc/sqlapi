# coding: utf-8
from app.sqlrest.util import cutout

class Where:
    ''' 条件解析 '''
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.opt_map = {
            "eq": "=", "gt": ">", "gte": ">=", "lt": "<", "lte": "<=", "neq": "!=", "like": "LIKE", "in": "IN", "is": "IS", "not": "NOT"
        }

    def to_sql(self):
        if self.key.upper() in ["AND", "OR"]:
            condition = f" {self.key.upper()} "
            value, match = cutout(r"\((.*)\)", self.value)
            if not match:
                raise ValueError("Invalid and or")
            key_val = [i.split("=") for i in match.split(",")]
            where_segment = [self.parse_where(i[0], i[1]) for i in key_val]
            segment = f"({condition.join(where_segment)})"
            return segment
        else:
            segment = self.parse_where(self.key, self.value)
            return segment

    def parse_where(self, key, value):
        if value.find(".") > 0:
            opt, value = value.split(".")
            if opt not in self.opt_map.keys():
                raise Exception("field error: where opt")
            if opt == "like":
                value = value.replace("*", "%")

            if not value.isdigit() and opt != 'in':
                value = f"'{value}'"

            return f"{key} {self.opt_map[opt]} {value}"
        else:
            return f"{key}='{value}'"
