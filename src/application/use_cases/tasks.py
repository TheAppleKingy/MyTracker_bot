from src.application.interfaces.task_repository import TaskRepositoryInterface
from src.domain.entities import Task


class ShowActiveTasks:
    def __init__(
        self,
        task_repo: TaskRepositoryInterface
    ):
        self._task_repo = task_repo

    async def execute(self, tg_name: str):
        return await self._task_repo.get_active_tasks(tg_name)


class ShowFinishedTasks:
    def __init__(
        self,
        task_repo: TaskRepositoryInterface
    ):
        self._task_repo = task_repo

    async def execute(self, tg_name: str):
        return await self._task_repo.get_finished_tasks(tg_name)


class CreateTask:
    pass
