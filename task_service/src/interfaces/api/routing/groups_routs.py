from fastapi import APIRouter, Depends

from domain.entities.users import User

from infra.security.permissions.permissions import IsActivePermission, GroupPermission

from application.service.group import GroupService
from application.dto.users_dto import UserView
from application.dto.groups_dto import GroupUpdate, GroupView

from ..dependencies import get_group_service, check_permissions


group_router = APIRouter(
    prefix='/api/groups',
    tags=['Groups']
)


@group_router.get('', response_model=list[GroupView])
async def get_groups(group_service: GroupService = Depends(get_group_service), request_user: User = Depends(check_permissions(GroupPermission(['Admin']), IsActivePermission()))):
    return await group_service.get_groups_and_users()


@group_router.patch('/{id}/add_users', response_model=list[UserView])
async def add_user_in_group(id: int, data: GroupUpdate, request_user: User = Depends(check_permissions(GroupPermission(['Admin']), IsActivePermission())), group_service: GroupService = Depends(get_group_service)):
    return await group_service.add_users(id, data.users)


@group_router.patch('/{id}/exclude_users', response_model=list[UserView])
async def exclude_users_from_group(id: int, data: GroupUpdate, request_user: User = Depends(check_permissions(GroupPermission(['Admin']), IsActivePermission())), group_service: GroupService = Depends(get_group_service)):
    return await group_service.exclude_users(id, data.users)
