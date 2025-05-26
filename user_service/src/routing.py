from fastapi import APIRouter, Depends, HTTPException

from schemas import UserCreateSchema, UserViewSchema

from user_service.src.models.users import User

from typing import List

from service.service import DBSocket

from dependencies import db_socket_dependency


user_router = APIRouter(
    prefix='/users',
    tags=['Users']
)


@user_router.post('')
async def create_user(user_data: UserCreateSchema, socket: DBSocket = Depends(db_socket_dependency(User))):
    await socket.create_db_obj(username=user_data.username, password=user_data.password)
    return {'detail': 'ok'}


@user_router.get('', response_model=List[UserViewSchema])
async def get_users(socket: DBSocket = Depends(db_socket_dependency(User))):
    users = await socket.get_all_db_objects()
    return users
