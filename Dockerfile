FROM python:3.7-slim
RUN sed -i 's/deb.debian.org/mirrors.ustc.edu.cn/g' /etc/apt/sources.list
RUN apt update
RUN apt install -y inetutils-ping vim telnet procps wait-for-it
RUN pip install -U pip

ADD requirements.txt .
RUN pip install -r requirements.txt -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com

USER root
WORKDIR /root/
ADD . .

RUN rm -rf UI/node_modules

EXPOSE 8000
CMD python3 server.py