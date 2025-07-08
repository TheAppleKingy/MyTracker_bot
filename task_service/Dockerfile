FROM python:3.12-alpine3.20

COPY task_service/src /src

WORKDIR /src
EXPOSE 8000

COPY ../../requirements.txt /temp/requirements.txt
RUN pip install -r /temp/requirements.txt
