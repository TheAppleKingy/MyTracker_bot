from typing import Optional

from fastapi import APIRouter, Depends, status

from application.dto.task_dto import TaskViewForUser
from application.service.task import TaskService
from application.dto.users_dto import UserCreate, UserView, UserUpdate

from domain.entities.users import User

from infra.db.repository.user_repo import UserRepository
from infra.security.permissions.permissions import GroupPermission, IsActivePermission

from ..dependencies import check_permissions, get_task_service, get_user_repo


user_router = APIRouter(
    prefix='/api/users',
    tags=['Users']
)


@user_router.post('', response_model=UserView, status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserCreate, request_user: User = Depends(check_permissions(GroupPermission(['Admin']), IsActivePermission())), user_repo: UserRepository = Depends(get_user_repo)):
    return await user_repo.create_user(**user_data.model_dump(exclude_none=True))


@user_router.get('', response_model=list[UserView])
async def get_users(request_user: User = Depends(check_permissions(GroupPermission(['Admin']), IsActivePermission())), user_repo: UserRepository = Depends(get_user_repo)):
    return await user_repo.get_users_by()


@user_router.get('/{id}', response_model=Optional[UserView])
async def get_user(id: int, request_user: User = Depends(check_permissions(GroupPermission(['Admin']), IsActivePermission())), user_repo: UserRepository = Depends(get_user_repo)):
    return await user_repo.get_user(id)


@user_router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(id: int, request_user: User = Depends(check_permissions(GroupPermission(['Admin']), IsActivePermission())), user_repo: UserRepository = Depends(get_user_repo)):
    await user_repo.delete_user(id)


@user_router.patch('/{id}', response_model=list[UserUpdate])
async def update_user(id: int, data_to_update: UserUpdate, request_user: User = Depends(check_permissions(GroupPermission(['Admin']), IsActivePermission())), user_repo: UserRepository = Depends(get_user_repo)):
    return await user_repo.update_user(id, **data_to_update.model_dump(exclude_none=True))


@user_router.get('/{id}/tasks', response_model=list[TaskViewForUser])
async def get_user_tasks(id: int, request_user: User = Depends(check_permissions(GroupPermission(['Admin']), IsActivePermission())), task_service: TaskService = Depends(get_task_service)):
    return await task_service.get_user_tasks_trees(id)
