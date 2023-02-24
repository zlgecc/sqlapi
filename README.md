# SQL api

> 部署一个基于mysql,sqlite的后端API，通过http请求自动生成增删改查SQL语句，进行对数据库的数据操作

## 启动

```bash
python server.py
```

## 使用

### 指定查询的 table
`/api/<table_name>`
> 查 user 表
> `/api/user`

### 查询数据 GET 方法
> GET方法
- $where（变量） 条件字段 
  * > 条件转义符
  ( eq, = ) 等于
  ( neq, <> ) 不等于
  ( gt, > ) 大于
  ( gte, >= ) 大于等于
  ( lt, < ) 小于
  ( lte, <= ) 小于等于
  ( like, LIKE ) 模糊查询
  ( in, IN ) 包含
  * name是xiaoming的数据: 
    `/api/user?name=xiaoming`
  * age大于18
    `/api/user?age=gt.18` 
  * 名字包含 zhang
    `/api/user?name=like.*zhang*`
  * 模糊匹配 zhang 或者年龄大于 18
    `/api/user?or=(name=like.*zhang*,age=gt.18)`
  * 模糊匹配 zhang 和者年龄大于 18
    `/api/user?and=(name=like.*zhang*,age=gt.18)`

- sort 排序
  * 按 created_at 倒序
    `/api/user?sort=-created_at`
  * 按 created_at 正序
    `/api/user?sort=created_at`

- page size 分页 （默认每页100条数据）
  * 第一页，每页 100 条数据
  `/api/user?page=1&size=100`

- field 查询字段
  * 指定查询字段
    `/api/user?field=id,name,age,created_at `
  * `:` 给字段重命名
    `/api/user?field=id,name:user_name`
  * `|` 给字段格式化, 支持int,str,float,json转化
    `/api/user?field=age|float` 返回时转 float
    `/api/json_data?field=data|json` 返回时字符串转 json

- 联表查询
  * `{}` 一对一关联查询，第一个值为联表条件（主表key=联表key）
  address{name,phone} 关联 address 表，查询 name, phone 字段
  `/api/user?field=id,name,address{address_id=id,name,phone}`
  ```json
  // 返回数据格式
  [{
    "id": 1,
    "name": "John",
    "address_id": 1,
    "address": {
      "id": 1,
      "name": "US",
      "phone": "xxxxxxxxxx"
    }
  }]
  ```
  * `[]` 一对多关联表查询，第一个值为联表条件（主表key=联表key）
  `/api/user?field=name,book[id=user_id,name,author]`
  ```json
  // 返回数据格式
  [{
    "id": 1,
    "name": "John",
    "book": [
      {
        "id": 1,
        "name": "《python machine learning》",
        "author": "xxx",
        "user_id": 1
      },
      {
        "id": 1,
        "name": "《javascript and vue》",
        "author": "xxx",
        "user_id": 1
      }
    ]
  }]
  ```

- 执行函数
  * 表总数函数：total
  `/api/user?meta=total`

### 新增数据 POST/PUT 方法

`/api/user`
```json
{
  "name": "zhangsan",
  "age": "30"
}
```

### 修改数据 POST/PUT 方法 

`api/user?id=2`
```json
{
  "name": "张三"
}
```

### 删除数据 DELETE 方法

删除id=2的数据
`api/user?id=2`
