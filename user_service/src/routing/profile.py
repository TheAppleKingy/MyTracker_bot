from fastapi.responses import JSONResponse
from fastapi.requests import Request
from fastapi import Depends, status, APIRouter, Security

from dependencies import db_socket_dependency, authenticate

from security.auth import refresh, access, login_user

from models.models import User

from schemas import UserCreateSchema

from service.service import DBSocket


profile_router = APIRouter(
    prefix='/api/profile',
    tags=['Profile']
)


@profile_router.post('/login')
async def login(user: User = Depends(login_user)):
    payload = {'user_id': user.id}
    access_token = access(payload)
    refresh_token = refresh(payload)
    response = JSONResponse(
        content={'detail': 'logged in', 'access': access_token})
    response.set_cookie('refresh', refresh_token)
    return response


@profile_router.post('/logout')
async def logout(user: User = Depends(authenticate)):
    print(user.email)
    return {'resp': 200}


@profile_router.post('/registration')
async def registration(reg_data: UserCreateSchema, socket: DBSocket = Depends(db_socket_dependency(User))):
    user = await socket.create_db_obj(**reg_data.model_dump())
    user.set_password()
    return user
