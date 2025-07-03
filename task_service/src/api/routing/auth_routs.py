from fastapi import Depends, status, APIRouter

from api.dependencies import get_user_auth_service, authenticate
from api.schemas.users_schemas import UserCreateSchema, UserViewSchema
from api.schemas.users_schemas import LoginSchema
from infra.security.jwt import get_token_for_user
from infra.db.models.users import User
from service.user_service import UserAuthService
from ..responses import response_cookies


profile_router = APIRouter(
    prefix='/api/profile',
    tags=['Profile']
)


@profile_router.post('/login')
async def login(login_data: LoginSchema, auth_service: UserAuthService = Depends(get_user_auth_service)):
    user = await auth_service.login_user(login_data)
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
async def registration(reg_data: UserCreateSchema, auth_service: UserAuthService = Depends(get_user_auth_service)):
    return await auth_service.register_user(reg_data)
