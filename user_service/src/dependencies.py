from service.service import SocketFactory, T, DBSocket

from fastapi import Depends

from database import get_db_session

from sqlalchemy.ext.asyncio import AsyncSession


def db_socket_dependency(model: T):
    async def socket(session: AsyncSession = Depends(get_db_session)):
        return DBSocket(model, session)
    return socket
