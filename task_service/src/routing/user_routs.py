from fastapi import APIRouter, Depends, status

from dependencies import get_user_allowed_by_group, get_user_service
from models.users import User
from service.user_service import UserService
from schemas.users_schemas import UserCreateSchema, UserViewSchema, UserUpdateSchema


user_router = APIRouter(
    prefix='/api/users',
    tags=['Users']
)


@user_router.post('', response_model=UserViewSchema, status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserCreateSchema, request_user: User = Depends(get_user_allowed_by_group('Admin')), user_service: UserService = Depends(get_user_service)):
    user = await user_service.create_user(**user_data.model_dump(exclude_none=True))
    user.set_password()
    return user


@user_router.get('', response_model=list[UserViewSchema])
async def get_users(request_user: User = Depends(get_user_allowed_by_group('Admin')), user_service: UserService = Depends(get_user_service)):
    users = await user_service.get_users()
    return users


@user_router.get('/{id}', response_model=UserViewSchema)
async def get_user(id: int, request_user: User = Depends(get_user_allowed_by_group('Admin')), user_service: UserService = Depends(get_user_service)):
    user = await user_service.get_user(User.id == id)
    return user


@user_router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(id: int, request_user: User = Depends(get_user_allowed_by_group('Admin')), user_service: UserService = Depends(get_user_service)):
    await user_service.delete_users(User.id == id)


@user_router.patch('/{id}', response_model=list[UserUpdateSchema])
async def update_user(id: int, data_to_update: UserUpdateSchema, request_user: User = Depends(get_user_allowed_by_group('Admin')), user_service: UserService = Depends(get_user_service)):
    updated = await user_service.update_users(User.id == id, **data_to_update.model_dump(exclude_none=True, exclude_unset=True))
    return updated
