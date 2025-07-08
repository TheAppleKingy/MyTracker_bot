from fastapi import Depends, status, APIRouter

from api.dependencies import get_user_auth_service, authenticate, check_permissions
from api.schemas.users_schemas import UserCreateSchema, ChangePasswordSchema
from api.schemas.users_schemas import LoginSchema
from infra.security.token.factory import TokenHandlerFactory as handler_factory
from infra.security.permissions.permissions import IsActivePermission
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
    jwt_handler = handler_factory.get_jwt_handler()
    token = jwt_handler.get_token_for_user(user)
    response = response_cookies({'detail': 'logged in'}, status.HTTP_200_OK, {
                                'token': token})
    return response


@profile_router.post('/logout')
async def logout(user: User = Depends(authenticate)):
    response = response_cookies(
        {'detail': 'logged out'}, status.HTTP_200_OK, cookies_data=['token'], delete=True)
    return response


@profile_router.post('/request/registration')
async def registration_request(reg_data: UserCreateSchema, auth_service: UserAuthService = Depends(get_user_auth_service)):
    await auth_service.registration_request(reg_data)
    return response_cookies({'detail': 'we sent email on your mail for confirm registration'}, status=status.HTTP_200_OK)


@profile_router.get('/confirm/registration/{confirm_token}')
async def confirm_registration(confirm_token: str, auth_service: UserAuthService = Depends(get_user_auth_service)):
    await auth_service.confirm_registration(confirm_token)
    return response_cookies({'detail': 'registration confirmed!'}, status.HTTP_200_OK)


@profile_router.get('/request/change_password')
async def change_password_request(auth_service: UserAuthService = Depends(get_user_auth_service), request_user: User = Depends(check_permissions(IsActivePermission()))):
    await auth_service.change_password_request(request_user.id)
    return response_cookies({'detail': 'we sent email on your mail for confirm change password'}, status=status.HTTP_200_OK)


@profile_router.post('/confirm/change_password/{confirm_token}')
async def confirm_change_password(confirm_token: str, change_password_schema: ChangePasswordSchema, auth_service: UserAuthService = Depends(get_user_auth_service), request_user: User = Depends(check_permissions(IsActivePermission()))):
    await auth_service.confirm_change_password(confirm_token, change_password_schema)
    return response_cookies({'detail': 'password was change successfully'}, status.HTTP_200_OK)
