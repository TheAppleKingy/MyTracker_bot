from fastapi import APIRouter, Depends, status

from dependencies import authenticate, get_task_service
from models.users import User
from models.tasks import Task
from service.task_service import TaskService
from schemas.task_schemas import TaskCreateSchema, TaskViewSchema, TaskUpdateSchema, TaskForUserSchema


bot_router = APIRouter(
    prefix='/api/bot',
    tags=['BOT']
)


@bot_router.get('/my_tasks', response_model=list[TaskForUserSchema])
async def get_my_tasks(user: User = Depends(authenticate), task_service: TaskService = Depends(get_task_service)):
    my_tasks = await task_service.get_objs(Task.user_id == user.id)
    return my_tasks
