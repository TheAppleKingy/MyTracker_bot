from typing import Sequence

from infra.db.models.tasks import Task
from infra.db.models.users import User
from infra.db.repository.task_repo import TaskRepository
from infra.db.repository.user_repo import UserRepository
from api.schemas.task_schemas import TaskCreateForUserSchema, TaskUpdateForUserSchema
from .exceptions import TaskServiceError


class TaskService:
    def __init__(self, task_repository: TaskRepository, user_repository: UserRepository):
        self.repo = task_repository
        self.user_repo = user_repository

    def check_is_root_task(self, task: Task):
        return not bool(task.task_id)

    def check_task_done(self, task: Task):
        return task.done and bool(task.pass_date)

    async def check_is_root_for_user(self, user_id: int, task_id: int):
        user_root_tasks = await self.get_root_tasks_for_user(user_id)
        target_task = await self.repo.get_task(task_id)
        print(user_root_tasks, target_task)
        if not target_task in user_root_tasks:
            raise TaskServiceError(
                f'Task ({target_task.title}) is not task for user ({user_id})')

    async def get_root_tasks_for_user(self, user_id: int) -> list[Task]:
        user = await self.user_repo.get_user_and_tasks(user_id)
        return [task for task in user.tasks if self.check_is_root_task(task)]

    async def get_full_trees(self, return_lists: bool = False):
        roots = await self.repo.get_root_tasks()
        ids = [root.id for root in roots]
        return await self.get_tasks_trees(ids, return_lists=return_lists)

    async def get_task_tree(self, from_task_id: Task, return_list: bool = False):
        """Returns root of task tree starts from task has id = from_task_id"""
        return await self.repo.get_nested_tasks(from_task_id, return_list=return_list)

    async def get_tasks_trees(self, from_task_ids: Sequence[int], return_lists: bool = False):
        return [await self.get_task_tree(task, return_list=return_lists) for task in from_task_ids]

    async def get_user_task_tree(self, user_id: int, root_task_id: int, return_list: bool = False):
        await self.check_is_root_for_user(user_id, root_task_id)
        return await self.get_task_tree(root_task_id, return_list=return_list)

    async def get_user_tasks_trees(self, user_id: int, return_lists: bool = False):
        roots = await self.get_root_tasks_for_user(user_id)
        root_ids = [task.id for task in roots]
        return await self.get_tasks_trees(root_ids, return_lists=return_lists)

    async def finish_task(self, task_id: int):
        tree = await self.get_task_tree(task_id, return_list=True)
        task = tree[0]
        not_finished_subtasks = []
        subtasks = tree[1:]
        for subtask in subtasks:
            if not self.check_task_done(subtask):
                not_finished_subtasks.append(str(subtask.id))
        if not_finished_subtasks:
            raise TaskServiceError(
                f'Cannot finish task ({task.title[:15]}) while not finished subtasks with next ids: {', '.join(not_finished_subtasks)}')
        finished = await self.repo.finish_task(task)
        return finished

    async def add_task_to_user(self, user_id: int, task_schema: TaskCreateForUserSchema):
        created = await self.repo.create_task(**task_schema.model_dump(exclude_none=True), user_id=user_id)
        return await self.get_user_task_tree(user_id, created.id)

    async def update_task_for_user(self, user_id: int, task_id: int, task_update_schema: TaskUpdateForUserSchema):
        user = await self.user_repo.get_user_and_tasks(user_id)
        if not any([task.id == task_id for task in user.tasks]):
            raise TaskServiceError(
                f'Task ({task_id}) does not belong to user ({user_id})')
        updated = await self.repo.update_task(task_id, **task_update_schema.model_dump(exclude_none=True))
        return await self.get_user_task_tree(user_id, updated.id)

    async def finish_task_for_user(self, user_id: int, task_id: int):
        task = await self.repo.get_task(task_id)
        if task.user_id != user_id:
            raise TaskServiceError(
                f'Task ({task.title[:15]}) does not belong to user with id ({user_id})')
        return await self.finish_task(task_id)
