from fastapi import APIRouter, Depends, status

from schemas import UserCreateSchema, UserViewSchema, UserUpdateSchema, GroupVeiwSchema, GroupUpdateSchema

from models.models import User, Group, users_groups
from service.service import DBSocket

from dependencies import db_socket_dependency, get_user_allowed_by_group, get_db_session

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


group_router = APIRouter(
    prefix='/api/groups',
    tags=['Groups']
)


@group_router.get('', response_model=list[GroupVeiwSchema])
async def get_groups(socket: DBSocket = Depends(db_socket_dependency(Group)), request_user: User = Depends(get_user_allowed_by_group('Admin'))):
    groups = await socket.get_db_objs()
    return groups


@group_router.patch('/{id}', response_model=GroupVeiwSchema)
async def add_user_in_group(id: int, data: GroupUpdateSchema, request_user: User = Depends(get_user_allowed_by_group('Admin')), group_socket: DBSocket = Depends(db_socket_dependency(users_groups)), user_socket: DBSocket = Depends(db_socket_dependency(User))):
    users_pks = data.users
    print(users_pks)
    users = await user_socket.get_db_objs(User.id.in_(users_pks))
    print(users)
    group = await group_socket.get_db_obj(Group.id == id)
    if users:
        for user in users:
            if not user in group.users:
                group.users.append(user)
        await group_socket.force_commit()
    return group
