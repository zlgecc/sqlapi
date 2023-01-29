

token="token: eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VybmFtZSI6ImFkbWluIiwidGltZXN0YW1wIjoxNjc0ODk3MzY3LCJ0cyI6MTY3NDg5NzM2N30.XrPpfUEUCCrD3At_YoZTyYbVMh3HLYIzbV0eOJqoJVw"


echo ">>> create table"
curl -H "$token" -X POST "http://localhost:8000/table?name=projects"
echo ">>> create table field"
curl -d '{"table":"projects", "field":"name", "type":"varchar(100)"}' -H "$token" -X POST "http://localhost:8000/table/field"


echo '>>> http query'
curl -H "$token" "http://localhost:8000/api/projects" 

echo '>>> http create'
curl -d '{"name": "test_http"}' -H "$token" -X POST  "http://localhost:8000/api/projects" 