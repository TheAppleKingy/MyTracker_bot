from typing import TypeVar, Sequence

from sqlalchemy import select, update, delete, insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import ColumnElement

from .utils import commitable, hashable


T = TypeVar('T')


class DBSocket:
    def __init__(self, model: T, session: AsyncSession):
        self.model: T = model
        self.session = session

    async def get_db_obj(self, *args: ColumnElement[bool]) -> T:
        query = select(self.model).where(*args)
        db_resp = await self.session.execute(query)
        return db_resp.scalar_one()

    async def get_db_objs(self, *args: ColumnElement[bool]) -> list[T]:
        query = select(self.model).where(*args)
        db_resp = await self.session.execute(query)
        return db_resp.scalars().all()

    @commitable
    async def delete_db_objs(self, *conditions: ColumnElement[bool]):
        query = delete(self.model).where(*conditions).returning(self.model)
        res = await self.session.execute(query)
        return res.scalars().all()

    @commitable
    async def update_db_objs(self, *conditions: ColumnElement[bool], **kwargs):
        query = update(self.model).where(
            *conditions).values(**kwargs).returning(self.model)
        res = await self.session.execute(query)
        updated = res.scalars().all()
        return updated

    @hashable(['password'])
    @commitable
    async def create_db_obj(self, **kwargs) -> T:
        query = insert(self.model).values(**kwargs).returning(self.model)
        res = await self.session.execute(query)
        obj = res.scalar_one()
        return obj

    @hashable(['password'])
    @commitable
    async def create_db_objs(self, raws: Sequence[dict]) -> list[T]:
        query = insert(self.model).values(raws).returning(self.model)
        res = await self.session.execute(query)
        objs = res.scalars().all()
        return objs


class SocketFactory:
    @classmethod
    def get_socket(cls, model: T, session: AsyncSession):
        return DBSocket(model, session)
