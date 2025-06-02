from fastapi import Depends, status, APIRouter

from dependencies import db_socket_dependency, authenticate, authenticate_by_refresh

from security.authentication import refresh, login_user, get_tokens_for_user

from models.models import User

from schemas import UserCreateSchema

from service.service import DBSocket

from . import response_cookies


profile_router = APIRouter(
    prefix='/api/profile',
    tags=['Profile']
)


@profile_router.post('/login')
async def login(user: User = Depends(login_user)):
    access_token, refresh_token = get_tokens_for_user(user)
    response = response_cookies({'detail': 'logged in'}, status.HTTP_200_OK, {
                                'access': access_token, 'refresh': refresh_token})
    return response


@profile_router.post('/logout')
async def logout(user: User = Depends(authenticate)):
    response = response_cookies({'detail': 'logged out'}, status.HTTP_200_OK, cookies_data=[
                                'access', 'refresh'], delete=True)
    return response


@profile_router.post('/registration', response_model=UserCreateSchema)
async def registration(reg_data: UserCreateSchema, socket: DBSocket = Depends(db_socket_dependency(User))):
    user = await socket.create_db_obj(**reg_data.model_dump())
    user.set_password()
    return user


@profile_router.get('/token')
async def token(user: User = Depends(authenticate_by_refresh)):
    access_token, refresh_token = get_tokens_for_user(user)
    response = response_cookies(
        cookies_data={'access': access_token, 'refresh': refresh_token})
    return response
