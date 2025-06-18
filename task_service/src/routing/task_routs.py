from fastapi import APIRouter, Depends, status

from dependencies import get_user_allowed_by_group, get_task_service, get_user_service
from models.users import User
from models.tasks import Task
from service.user_service import UserService
from service.task_service import TaskService
from schemas.task_schemas import TaskCreateSchema, TaskViewSchema, TaskUpdateSchema


task_router = APIRouter(
    prefix='/api/tasks',
    tags=['Tasks']
)


@task_router.post('', response_model=TaskViewSchema, status_code=status.HTTP_201_CREATED)
async def create_task(task_data: TaskCreateSchema, request_user: User = Depends(get_user_allowed_by_group('Admin')), task_service: TaskService = Depends(get_task_service)):
    task = await task_service.create_obj(**task_data.model_dump(exclude_none=True))
    return task


@task_router.get('', response_model=list[TaskViewSchema])
async def get_tasks(request_user: User = Depends(get_user_allowed_by_group('Admin')), task_service: TaskService = Depends(get_task_service)):
    tasks = await task_service.get_objs()
    return tasks


@task_router.get('/{id}', response_model=TaskViewSchema)
async def get_task(id: int, request_user: User = Depends(get_user_allowed_by_group('Admin')), task_service: TaskService = Depends(get_task_service)):
    task = await task_service.get_obj(Task.id == id, raise_exception=True)
    return task


@task_router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(id: int, request_user: User = Depends(get_user_allowed_by_group('Admin')), task_service: TaskService = Depends(get_task_service)):
    await task_service.delete(Task.id == id)


@task_router.patch('/{id}', response_model=list[TaskUpdateSchema])
async def update_task(id: int, data_to_update: TaskUpdateSchema, request_user: User = Depends(get_user_allowed_by_group('Admin')), task_service: TaskService = Depends(get_task_service)):
    updated = await task_service.update(Task.id == id, **data_to_update.model_dump(exclude_none=True, exclude_unset=True))
    return updated
