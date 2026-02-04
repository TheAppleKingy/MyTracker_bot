from datetime import datetime

from celery.result import AsyncResult

from src.application.interfaces.services import NotifyServiceInterface
from src.infra.tasks.notify import notify
from src.celery_app import celery_app


class CeleryNotifyService(NotifyServiceInterface):
    def send_notify(self, tg_name: str, task_id: int, message_text: str, chat_id: int, scheduled_time: datetime) -> str:
        async_res = notify.apply_async(args=[message_text, chat_id, tg_name, task_id], eta=scheduled_time)
        return async_res.id

    def revoke_reminder(self, id_: str) -> None:
        res = AsyncResult(id_, app=celery_app)
        res.revoke(terminate=True)
