from datetime import datetime

from src.application.interfaces.services import NotifyServiceInterface
from src.infra.tasks.notify import notify


class CeleryNotifyService(NotifyServiceInterface):
    def send_notify(self, message_text: str, chat_id: int, scheduled_time: datetime):
        notify.apply_async(args=[message_text, chat_id], eta=scheduled_time)
