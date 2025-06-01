from fastapi import APIRouter, Depends, HTTPException, status, Cookie

from schemas import UserCreateSchema, UserViewSchema, UserUpdateSchema

from models.models import User
from fastapi.requests import Request
from fastapi.responses import Response, JSONResponse
from service.service import DBSocket

from dependencies import db_socket_dependency


user_router = APIRouter(
    prefix='/api/users',
    tags=['Users']
)


@user_router.post('', response_model=UserViewSchema, status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserCreateSchema, socket: DBSocket = Depends(db_socket_dependency(User))):
    user = await socket.create_db_obj(**user_data.model_dump())
    user.set_password()
    return user


@user_router.get('', response_model=list[UserViewSchema])
async def get_users(socket: DBSocket = Depends(db_socket_dependency(User))):
    users = await socket.get_db_objs()
    return users


@user_router.get('/{id}', response_model=UserViewSchema)
async def get_user(id: int, socket: DBSocket = Depends(db_socket_dependency(User))):
    user = await socket.get_db_obj(User.id == id)
    return user


@user_router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(id: int, socket: DBSocket = Depends(db_socket_dependency(User))):
    await socket.delete_db_objs(User.id == id)


@user_router.patch('/{id}', response_model=list[UserUpdateSchema])
async def update_user(id: int, data_to_update: UserUpdateSchema, socket: DBSocket = Depends(db_socket_dependency(User))):
    updated = await socket.update_db_objs(User.id == id, **data_to_update.model_dump(exclude_none=True, exclude_unset=True))
    return updated
