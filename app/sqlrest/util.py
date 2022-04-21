# coding: utf-8

import re


# 匹配并抠出
def cutout(pattern, string):
    string = string.replace(" ", "")
    match = re.findall(pattern, string)
    if len(match) > 0:
        for i in match:
            string = string.replace(i, "")
        return string, match[0]
    return string, None

def symbol_split(string):
    ls = list()
    buff = ""
    enclosed = []
    symbol = ['(', ')', '[', ']', '{', '}']
    for i, val in enumerate(string):
        if i == len(string) - 1:
            buff += val
            ls.append(buff)
            buff = ""
        if val in symbol:
            index = symbol.index(val)
            if len(enclosed) > 0 and index - enclosed[-1] == 1:
                enclosed.pop()
            else:
                enclosed.append(index)
        if val == "," and len(enclosed) == 0:
            ls.append(buff)
            buff = ""
            continue
        buff += val
    return ls