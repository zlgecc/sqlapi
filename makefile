
image="zlgecc/sqlapi"

run:
	python server.py


# build docker image
build:
	docker build -t $(image) .
	docker push $(image)
	@echo $(image)
