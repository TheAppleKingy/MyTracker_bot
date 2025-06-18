from datetime import datetime, timezone

from models.users import User
from models.tasks import Task
from .exceptions import ServiceError
from .abstract import Service


class TaskService(Service[Task]):
    _target_model = Task

    def check_task_done(self, task: Task):
        if not (task.done and task.pass_date):
            raise ServiceError(f'Task "{task.title}" already finished')

    async def finish_task(self, task: Task):
        self.check_task_done(task)
        task.pass_date = datetime.now(timezone.utc)
        task.done = True
        await self.socket.force_commit()
        return task
