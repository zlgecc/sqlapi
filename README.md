# Rest API

> 快速部署一个后端 API， 通过 RESTful http 请求自动生成增删改查 SQL 语句，并对数据进行操作

## 启动

```bash
python server.py
```

## 查询数据

### 指定查询的 table

`/api/<table_name>`

> 查 user 表
> `/api/user`

### 查询关键字

| 关键字 | 作用                | 例子                       |
| :----: | ------------------- | -------------------------- |
|  sort  | 排序                | sort=weight,-craeted_at    |
| limit  | 数据个数 (默认 200) | limit=100                  |
| offset | 起始数据            | offset=0                   |
| group  | 聚合                | group=0                    |
| field  | 指定查询字段        | field=id,name              |
| $where | 条件字段            | name="xiaoming"&age=gte.25 |

### sort 排序

按 created_at 倒序排列
`/api/user?sort=-created_at`

按 ID 正序
`/api/user?sort=id`

### page size 分页

第一页，每页 100 条数据
`/api/user?page=1&size=100`
默认每页 100

### where 条件

符号表
| 符号 | 转译成 | | |
| ---- | ---- | ---- | ---- |
| eq| = | lte | <= |
| gt| > | neq | != |
| gte| >= | like | LIKE |
| lt| < | in | IN |
| lte| <= | is | IS |

例：`/api/user?name=xiaoming` 查 name 是 xiaoming

例：`/api/user?age=gt.18` 查 age 大于 18

例：`/api/user?name=like.*zhang*` 查名字包含 zhang

例：`/api/user?or=(name=like.*zhang*,age=gt.18`)` 模糊匹配 zhang 或者年龄大于 18

例：`/api/user?and=(name=like.*zhang*,age=gt.18`)` 模糊匹配 zhang 和者年龄大于 18

### field 查询字段

> 指定查询字段

`/api/user?field=id,name,age,created_at `

> 给字段重命名 `:`

`/api/user?field=id,name:user_name`

> 给字段格式转化 `|`

`/api/user?field=age|float` 返回时转 float

`/api/jsnon_data?field=data|json` 返回时字符串转 json

### 联表查询

1. 一对一关联查询

`/api/user?field=id,name,address{name,phone}`

> address{name,phone} 关联 address 表，查询 name, phone 字段

response:

```json
[
  {
    "id": 1,
    "name": "xiaoming",
    "address": {
      "name": "bj",
      "phone": "1777777777"
    }
  }
]
```

2. 一对多关联查询

`/api/user?field=id,name,order[price, id]`

> 符号为[]

response:

```json
[
  {
    "id": 1,
    "name": "xiaoming",
    "order": [
      {
        "price": 100,
        "id": 1232414151324
      },
      {
        "price": 100,
        "id": 1232414151324
      }
    ]
  }
]
```

### 执行函数

`/api/user?meta=total`

> 表总数函数： total

## 新增数据

### 使用 POST 方法

`/api/user`

```json
{
  "name": "zhangsan",
  "age": "30"
}
```

## 修改数据

### 使用 PUT 方法

`api/user?id=2`

```json
{
  "name": "张三"
}
```

## 删除数据

### 使用 DELETE 方法

`api/user?id=2`
