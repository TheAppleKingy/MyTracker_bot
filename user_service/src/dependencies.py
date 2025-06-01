from service.service import SocketFactory, T

from fastapi import Depends, Header
from fastapi.requests import Request

from database import get_db_session

from sqlalchemy.ext.asyncio import AsyncSession

from service.service import DBSocket

from models.models import User


def db_socket_dependency(model: T):
    async def socket(session: AsyncSession = Depends(get_db_session)):
        return SocketFactory.get_socket(model, session)
    return socket


async def authenticate(request: Request, Authorization: str = Header(default=None), socket: DBSocket = Depends(db_socket_dependency(User))):
    """dependency for getting authenticated by token user obj"""
    from security.auth import JWTAuther, extract_token
    print(request.headers)
    token = extract_token(Authorization)
    return await JWTAuther(socket).auth(token)
