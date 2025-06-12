from fastapi import Depends, status, APIRouter

from dependencies import jwt_authentication, get_user_service
from security.authentication import login_user, get_tokens_for_user
from models.users import User
from schemas.users_schemas import UserCreateSchema, UserViewSchema
from service.user_service import UserService
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
async def logout(user: User = Depends(jwt_authentication())):
    response = response_cookies({'detail': 'logged out'}, status.HTTP_200_OK, cookies_data=[
                                'access', 'refresh'], delete=True)
    return response


@profile_router.post('/registration', response_model=UserViewSchema)
async def registration(reg_data: UserCreateSchema, user_service: UserService = Depends(get_user_service)):
    user = await user_service.create_user(**reg_data.model_dump())
    user.set_password()
    await user_service.socket.force_commit()
    return user


@profile_router.get('/token')
async def token(user: User = Depends(jwt_authentication('refresh'))):
    access_token, refresh_token = get_tokens_for_user(user)
    response = response_cookies(
        cookies_data={'access': access_token, 'refresh': refresh_token})
    return response
