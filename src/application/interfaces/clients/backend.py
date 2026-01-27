from typing import Protocol, Union, Optional
from datetime import datetime

from src.domain.entities import Task


class BackendClientInterface(Protocol):
    async def register(self, tg_name: str) -> Union[str, None]: ...
    async def check_registered(self, tg_name: str) -> Union[str, bool]: ...

    async def create_task(
        self,
        title: str,
        description: str,
        deadline: datetime,
        parent_id: Optional[int] = None
    ) -> Task: ...
