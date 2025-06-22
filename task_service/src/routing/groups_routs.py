from fastapi import APIRouter, Depends

from dependencies import get_user_allowed_by_group, get_group_service, get_user_service
from models.users import User, Group
from service.group_service import GroupService
from service.user_service import UserService
from schemas.users_schemas import UserViewSchema
from schemas.groups_schemas import GroupUpdateSchema, GroupVeiwSchema
from service.abstract import check_objs_exist


group_router = APIRouter(
    prefix='/api/groups',
    tags=['Groups']
)


@group_router.get('', response_model=list[GroupVeiwSchema])
async def get_groups(group_service: GroupService = Depends(get_group_service), request_user: User = Depends(get_user_allowed_by_group('Admin'))):
    groups = await group_service.get_objs()
    return groups


@group_router.patch('/{id}/add_users', response_model=list[UserViewSchema])
async def add_user_in_group(id: int, data: GroupUpdateSchema, request_user: User = Depends(get_user_allowed_by_group('Admin')), group_service: GroupService = Depends(get_group_service), user_service: UserService = Depends(get_user_service)):
    users = await check_objs_exist(data.users, user_service)
    group = await group_service.get_obj(Group.id == id)
    added = await group_service.add_users(group, users)
    return added


@group_router.patch('/{id}/exclude_users', response_model=list[UserViewSchema])
async def exclude_users_from_group(id: int, data: GroupUpdateSchema, request_user: User = Depends(get_user_allowed_by_group('Admin')), group_service: GroupService = Depends(get_group_service), user_service: UserService = Depends(get_user_service)):
    users = await check_objs_exist(data.users, user_service)
    group = await group_service.get_obj(Group.id == id)
    excluded = await group_service.exclude_users(group, users)
    return excluded
