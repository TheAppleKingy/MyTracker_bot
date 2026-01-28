from asgiref.sync import async_to_sync
from aiogram import Bot
from dishka.integrations.celery import FromDishka

from src.celery_app import celery_app


@celery_app.task
def notify(text: str, chat_id: int, bot: FromDishka[Bot]):
    async_to_sync(bot.send_message)(chat_id, text)
