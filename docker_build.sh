# build docker image
registry="zlgecc/ra"

docker build -t $registry .

docker push $registry
echo $registry