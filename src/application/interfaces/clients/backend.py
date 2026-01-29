from typing import Protocol, Union, Optional
from datetime import datetime

from src.domain.entities import Task


class BackendClientInterface(Protocol):
    async def register(self, tg_name: str) -> Union[str, None]: ...
    async def check_registered(self, tg_name: str) -> bool: ...

    async def create_task(
        self,
        tg_name: str,
        title: str,
        description: str,
        deadline: datetime,
        parent_id: Optional[int] = None
    ) -> Task: ...

    async def get_active_tasks(
        self,
        tg_name: str,
        page: int = 1,
        size: int = 5
    ) -> tuple[int, int, list[Task]]: ...

    async def get_finished_tasks(
        self,
        tg_name: str,
        page: int = 1,
        size: int = 5
    ) -> tuple[int, int, list[Task]]: ...

    async def get_task(self, tg_name: str, task_id: int) -> Optional[Task]: ...
    async def delete_task(self, tg_name: str, task_id: int) -> None: ...
