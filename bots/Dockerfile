FROM python:3.12-alpine3.20

COPY /bots/src /src

WORKDIR /src
EXPOSE 8002

COPY ../../requirements.txt /temp/requirements.txt
RUN pip install -r /temp/requirements.txt