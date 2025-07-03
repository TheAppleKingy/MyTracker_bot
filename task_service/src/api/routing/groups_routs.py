from fastapi import APIRouter, Depends

from api.dependencies import get_group_service, for_admin_only
from infra.db.models.users import User
from service.group_service import GroupService
from api.schemas.users_schemas import UserViewSchema
from api.schemas.groups_schemas import GroupUpdateSchema, GroupVeiwSchema


group_router = APIRouter(
    prefix='/api/groups',
    tags=['Groups']
)


@group_router.get('', response_model=list[GroupVeiwSchema])
async def get_groups(group_service: GroupService = Depends(get_group_service), request_user: User = Depends(for_admin_only)):
    return await group_service.get_groups_and_users()


@group_router.patch('/{id}/add_users', response_model=list[UserViewSchema])
async def add_user_in_group(id: int, data: GroupUpdateSchema, request_user: User = Depends(for_admin_only), group_service: GroupService = Depends(get_group_service)):
    return await group_service.add_users(id, data.users)


@group_router.patch('/{id}/exclude_users', response_model=list[UserViewSchema])
async def exclude_users_from_group(id: int, data: GroupUpdateSchema, request_user: User = Depends(for_admin_only), group_service: GroupService = Depends(get_group_service)):
    return await group_service.exclude_users(id, data.users)
