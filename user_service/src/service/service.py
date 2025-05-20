from fastapi import Depends

from typing import TypeVar

from sqlalchemy import select, update, delete, insert
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db_session

from .utils import QueryFilterBuilderFabric


T = TypeVar('T')


def get_filter_builder(model: T):
    return QueryFilterBuilderFabric.get_build(model)


class DBSocket:
    def __init__(self, model: T, session: AsyncSession = Depends(get_db_session)):
        self.__model: T = model
        self.__session = session

    async def get_db_obj(self, _: tuple[bool] = Depends(get_filter_builder), **params) -> T:
        query = select(self.__model).where(*_(**params))
        db_resp = await self.__session.execute(query)
        return db_resp.scalar_one()

    async def get_db_objects(self, _: tuple[bool] = Depends(get_filter_builder), **params):
        query = select(self.__model).where(*_(**params))
        db_resp = await self.__session.execute(query)
        return db_resp.scalars().all()

    async def get_all_db_objects(self):
        query = select(self.__model)
        db_resp = await self.__session.execute(query)
        return db_resp.scalars().all()

    async def delete_db_obj(self, _: tuple[bool] = Depends(get_filter_builder), **params):
        query = delete(self.__model).where(*_(**params))
        await self.__session.execute(query)

    async def update_db_objs(self, _: tuple[bool] = Depends(get_filter_builder), **params):
        query = update(self.__model).where(*_(**params))
        await self.__session.execute(query)

    async def create_db_obj(self, _: tuple[bool] = Depends(get_filter_builder), **params):
        obj = self.__model(**params)
        self.__session.add(obj)


class SocketFactory:
    @classmethod
    def get_socket(cls, model: T):
        return DBSocket(model)


def get_socket(model: T):
    return SocketFactory.get_socket(model)
