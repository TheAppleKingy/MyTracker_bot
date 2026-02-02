from asgiref.sync import async_to_sync
from aiogram import Bot
from dishka.integrations.celery import FromDishka

from src.application.interfaces.storage import StorageInterface
from src.celery_app import celery_app


@celery_app.task(bind=True)
def notify(
    self,
    text: str,
    chat_id: int,
    tg_name: str,
    bot: FromDishka[Bot],
    storage: FromDishka[StorageInterface],
):
    try:
        async_to_sync(bot.send_message)(chat_id, text, parse_mode="HTML")
    finally:
        async_to_sync(storage.delete_reminder)(tg_name, self.request.id)
