# coding: utf-8

from sqlrest import util


class Where:

    # parse
    def __init__(self, base_table):
        self.table   = base_table
        self.where   = []
        self.opt_map = {
            "eq"  : "=",
            "gt"  : ">",
            "gte" : ">=",
            "lt"  : "<",
            "lte" : "<=",
            "neq" : "!=",
            "like": "LIKE",
            "in"  : "IN",
            "is"  : "IS",
            "not" : "NOT"
        }

    def parse(self, key, value):
        # and or 语法
        if key.upper() in ["AND", "OR"]:
            condition = f" {key.upper()} "
            value, match = util.cutout(r"\((.*)\)", value)
            if not match:
                raise ValueError("Invalid and or")
            key_val = [i.split("=") for i in match.split(",")]
            where_segment = [self.parse_where(i[0], i[1]) for i in key_val]
            segment = f"({condition.join(where_segment)})"
            self.where.append(segment)
        else:
            segment = self.parse_where(key, value)
            self.where.append(segment)


    def parse_where(self, key, value):
        # 去空格
        value = value.replace(' ', '')
        key = self.table_field(key)
        if value.find(".") > 0:
            opt, value = value.split(".")
            if opt not in self.opt_map.keys():
                raise ValueError("field error: where opt")
            if opt == "like":
                value = value.replace("*", "%")
                return f"{key} {self.opt_map[opt]} '{value}'"
            else:
                return f"{key} {self.opt_map[opt]} {value}"
        else:
            return f"{key}='{value}'"

    def to_variable(self):
        return " AND ".join(self.where)

    def table_field(self, field):
        if  field.find("(") != -1:
            return field
        if field.find(".") < 0:
            return f"{self.table}.{field}"
        return field
