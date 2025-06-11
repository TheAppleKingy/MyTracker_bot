from fastapi import APIRouter, Depends

from dependencies import get_user_allowed_by_group, get_group_service, get_user_service
from models.users import User, Group
from service.group_service import GroupService
from service.user_service import UserService
from schemas.users_schemas import UserViewSchema
from schemas.groups_schemas import GroupUpdateSchema, GroupVeiwSchema


group_router = APIRouter(
    prefix='/api/groups',
    tags=['Groups']
)


@group_router.get('', response_model=list[GroupVeiwSchema])
async def get_groups(group_service: GroupService = Depends(get_group_service), request_user: User = Depends(get_user_allowed_by_group('Admin'))):
    groups = await group_service.get_groups()
    return groups


@group_router.patch('/{id}', response_model=list[UserViewSchema])
async def add_user_in_group(id: int, data: GroupUpdateSchema, request_user: User = Depends(get_user_allowed_by_group('Admin')), group_service: GroupService = Depends(get_group_service), user_service: UserService = Depends(get_user_service)):
    users = await user_service.get_users(User.id.in_(data.users))
    print(users, 'users_here')
    group = await group_service.get_group(Group.id == id)
    print(group, 'group here')
    added = await group_service.add_users(group, users)
    return added


@group_router.patch('/{id}', response_model=list[UserViewSchema])
async def exclude_users_from_group(id: int, data: GroupUpdateSchema, request_user: User = Depends(get_user_allowed_by_group('Admin')), group_service: GroupService = Depends(get_group_service), user_service: UserService = Depends(get_user_service)):
    users = await user_service.get_users(User.id.in_(data.users))
    group = await group_service.get_group(Group.id == id)
    excluded = await group_service.exclude_users(group, users)
    return excluded
