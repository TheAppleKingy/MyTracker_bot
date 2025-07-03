from datetime import datetime, timezone

from sqlalchemy import text
from sqlalchemy.orm import selectinload

from ..models.tasks import Task
from .base import InitRepo
from .exceptions import TaskRepositoryError


class TaskRepository(InitRepo):
    _model = Task

    async def get_task(self, id: int) -> Task | None:
        return await self._repo.get_db_obj(Task.id == id)

    async def get_task_with_user(self, id: int) -> Task | None:
        return await self._repo.get_db_obj(Task.id == id, options=[selectinload(Task.user)])

    async def get_root_tasks(self) -> list[Task]:
        return await self._repo.get_db_objs(Task.task_id == None)

    async def create_task(self, **task_data) -> Task:
        return await self._repo.create_db_obj(**task_data)

    async def delete_task(self, id: int) -> Task:
        return await self._repo.delete_db_objs(Task.id == id)

    async def update_task(self, id: int, **kwargs) -> Task:
        return await self._repo.update_db_objs(Task.id == id, **kwargs)

    async def get_nested_tasks(self, from_task_id: int, return_list: bool = False) -> Task | list[Task]:
        query = text(f"""WITH RECURSIVE task_tree AS (
            SELECT * FROM tasks WHERE id = {from_task_id}
            UNION ALL
            SELECT t.* FROM tasks t
            INNER JOIN task_tree tt ON t.task_id = tt.id
        )
        SELECT * FROM task_tree;""")
        res = await self._repo.execute_query(query)
        tasks_data = res.mappings().all()
        if not tasks_data:
            raise TaskRepositoryError(f'Task does not exist')
        ids = [task_data['id'] for task_data in tasks_data]
        tasks_objs = await self._repo.get_db_objs(Task.id.in_(ids), options=[selectinload(Task.subtasks)])
        task_map = {task.id: task for task in tasks_objs}
        ordered = [task_map[id_] for id_ in ids]
        if return_list:
            return ordered
        return ordered[0]

    async def finish_task(self, task: Task):
        if task.done:
            raise TaskRepositoryError(
                f'Task ({task.id}) already passed')
        task.pass_date = datetime.now(timezone.utc)
        task.done = True
        await self._repo.force_commit()
        return task
