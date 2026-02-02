from typing import Protocol
from datetime import datetime


class NotifyServiceInterface(Protocol):
    def send_notify(
        self,
        tg_name: str,
        message_text: str,
        chat_id: int,
        scheduled_time: datetime
    ) -> str: ...
    def revoke_reminder(self, id_: str) -> None: ...
