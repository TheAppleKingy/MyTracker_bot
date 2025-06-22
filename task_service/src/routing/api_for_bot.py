from fastapi import APIRouter, Depends, status

from dependencies import authenticate, get_task_service
from models.users import User
from models.tasks import Task
from service.task_service import TaskService
from schemas.task_schemas import TaskCreateSchema, TaskViewSchema, TaskUpdateSchema, TaskForUserSchema, TaskCreateForUserSchema


bot_router = APIRouter(
    prefix='/api/bot',
    tags=['BOT']
)


@bot_router.get('/my_tasks', response_model=list[TaskForUserSchema])
async def get_my_tasks(user: User = Depends(authenticate), task_service: TaskService = Depends(get_task_service)):
    trees = await task_service.get_user_tasks_trees(user)
    return trees


@bot_router.post('/create_task', response_model=TaskCreateForUserSchema)
async def create_task(task_data: TaskCreateForUserSchema, user: User = Depends(authenticate), task_service: TaskService = Depends(get_task_service)):
    task = await task_service.create_obj(**task_data.model_dump(exclude_none=True), user_id=user.id)
    return task


@bot_router.patch('/update_task/{id}', response_model=TaskUpdateSchema)
async def update_task(id: int, data: TaskUpdateSchema, user: User = Depends(authenticate), task_service: TaskService = Depends(get_task_service)):
    data.user_id = user.id
    updated = await task_service.update(Task.id == id, **data.model_dump(exclude_none=True))
    return updated


@bot_router.delete('/finish_task/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def finish_task(id: int,  user: User = Depends(authenticate), task_service: TaskService = Depends(get_task_service)):
    to_finish = await task_service.get_obj(Task.id == id, raise_exception=True)
    finished = await task_service.finish_user_task(user, to_finish)
    return finished
