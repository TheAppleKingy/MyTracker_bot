from typing import Protocol
from datetime import datetime


class NotifyServiceInterface(Protocol):
    async def send_notify(
        self,
        tg_name: str,
        task_id: int,
        message_text: str,
        chat_id: int,
        scheduled_time: datetime
    ) -> str: ...
    def revoke_reminder(self, id_: str) -> None: ...
