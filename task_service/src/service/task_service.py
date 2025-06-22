from datetime import datetime, timezone
from typing import Sequence

from sqlalchemy import text
from sqlalchemy.orm import selectinload

from models.users import User
from models.tasks import Task
from .exceptions import ServiceError
from .abstract import Service


class TaskService(Service[Task]):
    _target_model = Task

    def check_is_root_task(self, task: Task):
        return not bool(task.task_id)

    def get_root_tasks_for_user(self, user: User):
        return [task for task in user.tasks if self.check_is_root_task(task)]

    def check_is_root_for_user(self, user: User, task: Task):
        user_tasks = self.get_root_tasks_for_user(user)
        if not task in user_tasks:
            raise ServiceError(
                f'Task ({task.title}) is not task for user ({user.tg_name})')

    async def get_root_tasks(self):
        return await self.get_objs(self._target_model.task_id == None)

    async def get_task_tree(self, from_task: Task, return_root: bool = True):
        """If return_root == True, method return only root of tree, otherwise return list of all nested tasks starts from from_task(nested fields are set in both cases)"""
        query = text(f"""WITH RECURSIVE task_tree AS (
            SELECT * FROM tasks WHERE id = {from_task.id}
            UNION ALL
            SELECT t.* FROM tasks t
            INNER JOIN task_tree tt ON t.task_id = tt.id
        )
        SELECT * FROM task_tree;""")
        res = await self.socket.session.execute(query)
        tasks_data = res.mappings().all()
        ids = [task_data['id'] for task_data in tasks_data]
        tasks_objs = await self.get_objs(self._target_model.id.in_(ids), options=[selectinload(self._target_model.subtasks)])
        if return_root:
            return tasks_objs[0]
        return tasks_objs

    async def get_tasks_trees(self, from_tasks: Sequence[Task], return_roots: bool = True):
        if return_roots:
            return [await self.get_task_tree(task) for task in from_tasks]
        return [await self.get_task_tree(task, return_root=return_roots) for task in from_tasks]

    async def get_user_task_tree(self, user: User, root_task: Task, return_root: bool = True):
        self.check_is_root_for_user(user, root_task)
        if return_root:
            return await self.get_task_tree(root_task)
        return await self.get_task_tree(root_task, return_root=return_root)

    async def get_user_tasks_trees(self, user: User, return_roots: bool = True):
        roots = self.get_root_tasks_for_user(user)
        if return_roots:
            return await self.get_tasks_trees(roots)
        return await self.get_tasks_trees(roots, return_roots=return_roots)

    def check_task_done(self, task: Task):
        return task.done and bool(task.pass_date)

    async def finish_task(self, task: Task):
        if self.check_task_done(task):
            raise ServiceError(f'Task ({task.title}) already finished')
        not_finished_subtasks = []
        nested_tasks = await self.get_task_tree(task, return_root=False)
        subtasks = nested_tasks[1:]
        for subtask in subtasks:
            if not self.check_task_done(subtask) and subtask.task_id == task.id:
                not_finished_subtasks.append(str(subtask.id))
        if not_finished_subtasks:
            raise ServiceError(
                f'Cannot finish task ({task.title}) while not finished subtasks with next ids: {', '.join(not_finished_subtasks)}')
        task.pass_date = datetime.now(timezone.utc)
        task.done = True
        await self.socket.force_commit()
        return task

    async def finish_user_task(self, user: User, task: Task):
        if task.user_id != user.id:
            raise ServiceError(
                f'User ({user.tg_name}) has no task with title ({task.title})')
        return await self.finish_task(task)
