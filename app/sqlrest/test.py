
from pprint import pprint
from app.sqlrest.query import Query

query_list = [
    ['user', "field=id,name,car[id,brand]"],
    ['car', "field=id,name,user{id,name}"],
    ['user', "field=id,name,car[id,name],driving_license[id,name]"],
    ['car', "field=id,name,user{id,name}"],
    ['car', "field=id:iii,name,user{id,name}"],
    ['jobs', "field=id,name,projects{project_id=id,name}&id=81500331"],
    ['projects', "field=id,name,jobs[id=project_id,%20name]"],
]

def testQuery():
    for item in query_list:
        query = Query(*item)
        print("=====sql====>", query.to_sql())

if __name__ == '__main__':
    testQuery()