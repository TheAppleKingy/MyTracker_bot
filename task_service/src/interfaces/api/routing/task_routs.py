from fastapi import APIRouter, Depends, status

from application.dto.task_dto import TaskCreate, TaskView, TaskUpdate, TaskTree
from application.service.task import TaskService

from domain.entities.users import User

from infra.db.repository.task_repo import TaskRepository
from infra.security.permissions.permissions import IsActivePermission, GroupPermission

from ..dependencies import get_task_service, get_task_repo, check_permissions


task_router = APIRouter(
    prefix='/api/tasks',
    tags=['Tasks']
)


@task_router.post('', response_model=TaskView, status_code=status.HTTP_201_CREATED)
async def create_task(task_data: TaskCreate, request_user: User = Depends(check_permissions(GroupPermission(['Admin']), IsActivePermission())), task_repo: TaskRepository = Depends(get_task_repo)):
    return await task_repo.create_task(**task_data.model_dump(exclude_none=True))


@task_router.get('/trees', response_model=list[TaskTree])
async def get_tasks_trees(request_user: User = Depends(check_permissions(GroupPermission(['Admin']), IsActivePermission())), task_service: TaskService = Depends(get_task_service)):
    return await task_service.get_full_trees()


@task_router.get('/{id}', response_model=TaskView)
async def get_task(id: int, request_user: User = Depends(check_permissions(GroupPermission(['Admin']), IsActivePermission())), task_repo: TaskRepository = Depends(get_task_repo)):
    return await task_repo.get_task(id)


@task_router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(id: int, request_user: User = Depends(check_permissions(GroupPermission(['Admin']), IsActivePermission())), task_repo: TaskRepository = Depends(get_task_repo)):
    await task_repo.delete_task(id)


@task_router.patch('/{id}', response_model=list[TaskUpdate])
async def update_task(id: int, data_to_update: TaskUpdate, request_user: User = Depends(check_permissions(GroupPermission(['Admin']), IsActivePermission())), task_repo: TaskRepository = Depends(get_task_repo)):
    return await task_repo.update_task(id, **data_to_update.model_dump(exclude_none=True))
