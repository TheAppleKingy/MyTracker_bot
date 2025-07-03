from typing import Optional

from fastapi import APIRouter, Depends, status

from api.dependencies import for_admin_only, get_user_service, get_task_service, get_user_repo
from api.schemas.task_schemas import TaskViewForUserSchema
from infra.db.models.users import User
from infra.db.repository.user_repo import UserRepository
from service.user_service import UserService
from service.task_service import TaskService
from api.schemas.users_schemas import UserCreateSchema, UserViewSchema, UserUpdateSchema


user_router = APIRouter(
    prefix='/api/users',
    tags=['Users']
)


@user_router.post('', response_model=UserViewSchema, status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserCreateSchema, request_user: User = Depends(for_admin_only), user_repo: UserRepository = Depends(get_user_repo)):
    return await user_repo.create_user(**user_data.model_dump(exclude_none=True))


@user_router.get('', response_model=list[UserViewSchema])
async def get_users(request_user: User = Depends(for_admin_only), user_repo: UserRepository = Depends(get_user_repo)):
    return await user_repo.get_users_by()


@user_router.get('/{id}', response_model=Optional[UserViewSchema])
async def get_user(id: int, request_user: User = Depends(for_admin_only), user_repo: UserRepository = Depends(get_user_repo)):
    return await user_repo.get_user(id)


@user_router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(id: int, request_user: User = Depends(for_admin_only), user_repo: UserRepository = Depends(get_user_repo)):
    await user_repo.delete_user(id)


@user_router.patch('/{id}', response_model=list[UserUpdateSchema])
async def update_user(id: int, data_to_update: UserUpdateSchema, request_user: User = Depends(for_admin_only), user_repo: UserRepository = Depends(get_user_repo)):
    return await user_repo.update_user(id, **data_to_update.model_dump(exclude_none=True))


@user_router.get('/{id}/tasks', response_model=list[TaskViewForUserSchema])
async def get_user_tasks(id: int, request_user: User = Depends(for_admin_only), task_service: TaskService = Depends(get_task_service)):
    res = await task_service.get_user_tasks_trees(id)
    return res
