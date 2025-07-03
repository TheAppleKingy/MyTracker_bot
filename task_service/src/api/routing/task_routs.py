from fastapi import APIRouter, Depends, status

from api.dependencies import for_admin_only, get_task_service, get_task_repo
from infra.db.models.users import User
from infra.db.repository.task_repo import TaskRepository
from service.task_service import TaskService
from api.schemas.task_schemas import TaskCreateSchema, TaskViewSchema, TaskUpdateSchema, TaskTreeSchema


task_router = APIRouter(
    prefix='/api/tasks',
    tags=['Tasks']
)


@task_router.post('', response_model=TaskViewSchema, status_code=status.HTTP_201_CREATED)
async def create_task(task_data: TaskCreateSchema, request_user: User = Depends(for_admin_only), task_repo: TaskRepository = Depends(get_task_repo)):
    return await task_repo.create_task(**task_data.model_dump(exclude_none=True))


@task_router.get('/trees', response_model=list[TaskTreeSchema])
async def get_tasks_trees(request_user: User = Depends(for_admin_only), task_service: TaskService = Depends(get_task_service)):
    return await task_service.get_full_trees()


@task_router.get('/{id}', response_model=TaskViewSchema)
async def get_task(id: int, request_user: User = Depends(for_admin_only), task_repo: TaskRepository = Depends(get_task_repo)):
    return await task_repo.get_task(id)


@task_router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(id: int, request_user: User = Depends(for_admin_only), task_repo: TaskRepository = Depends(get_task_repo)):
    await task_repo.delete_task(id)


@task_router.patch('/{id}', response_model=list[TaskUpdateSchema])
async def update_task(id: int, data_to_update: TaskUpdateSchema, request_user: User = Depends(for_admin_only), task_repo: TaskRepository = Depends(get_task_repo)):
    return await task_repo.update_task(id, **data_to_update.model_dump(exclude_none=True))
