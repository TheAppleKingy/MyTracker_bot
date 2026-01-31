from typing import Protocol
from datetime import datetime


class NotifyServiceInterface(Protocol):
    def send_notify(self, message_text: str, chat_id: int, scheduled_time: datetime): ...
