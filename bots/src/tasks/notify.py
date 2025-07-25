import config

from asgiref.sync import async_to_sync

from aiogram import Bot

from celery_app import celery
from api.schemas import TaskViewSchema

bot = Bot(config.TOKEN)


@celery.task(queue=config.QUEUE)
def notify(task_title: str, remained_time: str, chat_id: int):
    async_to_sync(bot.send_message)(
        chat_id, f'Task "{task_title[:15]}..." is waiting! Deadline over ' + remained_time)
