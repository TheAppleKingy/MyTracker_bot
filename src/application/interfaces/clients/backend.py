from typing import Protocol, Union, Optional, Literal, Any, Generic, TypeVar
from datetime import datetime

from src.domain.entities import Task, TaskPreview

T = TypeVar('T')

# BackendResponse теперь generic
BackendResponse = tuple[bool, Union[str, T]]


class BackendClientInterface(Protocol):
    async def register(self, tg_name: str) -> BackendResponse[Optional[str]]: ...
    async def check_registered(self, tg_name: str) -> BackendResponse[bool]: ...

    async def create_task(
        self,
        tg_name: str,
        title: str,
        description: str,
        deadline: datetime,
        parent_id: Optional[int] = None
    ) -> BackendResponse[Task]: ...

    async def get_task(self, tg_name: str, task_id: int) -> BackendResponse[Task]: ...
    async def delete_task(self, tg_name: str, task_id: int) -> BackendResponse[None]: ...

    async def get_subtasks(
        self,
        tg_name: str,
        status: Literal["active", "finished"],
        parent_id: int,
        page: int = 1,
        size: int = 5
    ) -> BackendResponse[tuple[int, int, list[TaskPreview]]]: ...

    async def get_tasks(
        self,
        tg_name: str,
        status: Literal["active", "finished"],
        page: int = 1,
        size: int = 5
    ) -> BackendResponse[tuple[int, int, list[TaskPreview]]]: ...

    async def update_task(
        self,
        tg_name: str,
        task_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None,
        deadline: Optional[datetime] = None
    ) -> BackendResponse[TaskPreview]: ...

    async def finish_task(self, tg_name: int, task_id: int) -> BackendResponse[None]: ...
    async def force_finish_task(self, tg_name: int, task_id: int) -> BackendResponse[None]: ...
    async def check_task_active(self, tg_name: str, task_id: int) -> BackendResponse[bool]: ...
    async def get_parent_id(self, tg_name: int, task_id: int) -> BackendResponse[Optional[int]]: ...
