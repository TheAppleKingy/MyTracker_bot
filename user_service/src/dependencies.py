from service.service import SocketFactory, T

from fastapi import Depends, Cookie

from database import get_db_session

from sqlalchemy.ext.asyncio import AsyncSession

from service.service import DBSocket

from models.models import User, Group


def db_socket_dependency(model: T):
    async def socket(session: AsyncSession = Depends(get_db_session)):
        return SocketFactory.get_socket(model, session)
    return socket


async def authenticate(access: str = Cookie(default=None, include_in_schema=False), socket: DBSocket = Depends(db_socket_dependency(User))):
    """dependency for getting authenticated by token user obj"""
    from security.authentication import JWTAuther
    return await JWTAuther(socket).auth(access)


async def authenticate_by_refresh(refresh: str = Cookie(default=None, include_in_schema=False), socket: DBSocket = Depends(db_socket_dependency(User))):
    from security.authentication import JWTAuther
    return await JWTAuther(socket).auth(refresh, 'refresh')


def get_user_allowed_by_group(allowed_group: str):
    async def check_user(user: User = Depends(authenticate), socket: DBSocket = Depends(db_socket_dependency(Group))):
        from permissions import GroupPermission
        return await GroupPermission(allowed_group, socket).check(user)
    return check_user
