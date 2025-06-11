FROM python:3.12-slim

COPY worker/ /app
COPY task_service/src/ /app/task_service
COPY bots/src/ /app/bots

WORKDIR /app

COPY ../../requirements.txt /temp/requirements.txt
RUN pip install -r /temp/requirements.txt

CMD celery -A celery_app.celery worker --loglevel=info --concurrency=${CELERY_WORKERS}