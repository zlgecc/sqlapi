# build docker image
registry="zlgecc/sra"

docker build -t $registry .

docker push $registry
echo $registry