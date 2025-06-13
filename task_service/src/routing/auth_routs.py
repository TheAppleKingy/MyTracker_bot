from fastapi import Depends, status, APIRouter

from dependencies import jwt_authentication, get_user_service, authenticate
from security.authentication import login_user, get_token_for_user
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
    token = get_token_for_user(user)
    response = response_cookies({'detail': 'logged in'}, status.HTTP_200_OK, {
                                'token': token})
    return response


@profile_router.post('/logout')
async def logout(user: User = Depends(authenticate)):
    response = response_cookies(
        {'detail': 'logged out'}, status.HTTP_200_OK, cookies_data=['token'], delete=True)
    return response


@profile_router.post('/registration', response_model=UserViewSchema)
async def registration(reg_data: UserCreateSchema, user_service: UserService = Depends(get_user_service)):
    user = await user_service.create_obj(**reg_data.model_dump())
    return user
