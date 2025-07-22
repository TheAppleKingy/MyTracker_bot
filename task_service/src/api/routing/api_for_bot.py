from fastapi import APIRouter, Depends, status

from api.dependencies import authenticate, get_task_service, get_user_auth_service
from infra.db.models.users import User
from service.task_service import TaskService
from service.user_service import UserAuthService
from api.schemas.task_schemas import TaskUpdateSchema, TaskViewForUserSchema, TaskCreateForUserSchema, TaskUpdateForUserSchema
from api.schemas.users_schemas import CheckIsActiveSchema


bot_router = APIRouter(
    prefix='/api/bot',
    tags=['BOT']
)


@bot_router.post('/check_is_active')
async def check_is_active(check_is_active_schema: CheckIsActiveSchema, user_service: UserAuthService = Depends(get_user_auth_service)):
    await user_service.check_user_active(check_is_active_schema.tg_name)


@bot_router.get('/my_tasks', response_model=list[TaskViewForUserSchema])
async def get_my_tasks(user: User = Depends(authenticate), task_service: TaskService = Depends(get_task_service)):
    return await task_service.get_user_tasks_trees(user.id)


@bot_router.get('/my_task/{id}', response_model=TaskViewForUserSchema)
async def get_my_task(id: int, user: User = Depends(authenticate), task_service: TaskService = Depends(get_task_service)):
    return await task_service.get_task_tree(id)


@bot_router.post('/create_task', response_model=TaskViewForUserSchema)
async def create_task(task_data: TaskCreateForUserSchema, user: User = Depends(authenticate), task_service: TaskService = Depends(get_task_service)):
    return await task_service.add_task_to_user(user.id, task_data)


@bot_router.patch('/update_task/{id}', response_model=TaskViewForUserSchema)
async def update_task(id: int, data: TaskUpdateForUserSchema, user: User = Depends(authenticate), task_service: TaskService = Depends(get_task_service)):
    return await task_service.update_task_for_user(user.id, id, data)


@bot_router.delete('/finish_task/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def finish_task(id: int,  user: User = Depends(authenticate), task_service: TaskService = Depends(get_task_service)):
    await task_service.finish_task_for_user(user.id, id)
