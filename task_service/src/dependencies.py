from fastapi import Depends, Cookie
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db_session
from repository.socket import DBSocket, SocketFactory, T
from service.factories import UserServiceFactory, GroupServiceFactory
from service.user_service import UserService
from service.group_service import GroupService
from models.users import User, Group


def get_socket(model: T):
    async def socket(session: AsyncSession = Depends(get_db_session)):
        return SocketFactory.get_socket(model, session)
    return socket


def get_user_service(socket: DBSocket = Depends(get_socket(User))):
    service = UserServiceFactory.get_service(socket)
    return service


def get_group_service(socket: DBSocket = Depends(get_socket(Group))):
    service = GroupServiceFactory.get_service(socket)
    return service


async def authenticate(token: str = Cookie(default=None, include_in_schema=False), user_service: UserService = Depends(get_user_service)):
    from security.authentication import JWTAuther
    return await JWTAuther(user_service).auth(token)


def get_user_allowed_by_group(allowed_group: str):
    async def check_user(user: User = Depends(authenticate), group_service: GroupService = Depends(get_group_service)):
        from permissions import GroupPermission
        return await GroupPermission(allowed_group, group_service).check(user)
    return check_user
