from typing import Callable, TypeVar, Sequence
from abc import ABC, abstractmethod

from sqlalchemy import select, update, delete, insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import ColumnElement
from sqlalchemy.orm.attributes import InstrumentedAttribute


T = TypeVar('T')


def commitable(commitable_method: Callable):
    """This decorator provides opportunity to commit changes in db after calling DBSocket methods. Changes will be commited by default. If don't need commit changes set "commit=False" """

    async def commit(self: Socket, *args, **kwargs):
        commit = kwargs.pop('commit', True)
        res = await commitable_method(self, *args, **kwargs)
        if commit:
            await self.session.commit()
        return res
    return commit


class Socket(ABC):
    def __init__(self, model: T, session: AsyncSession):
        self.model: T = model
        self.session = session

    @abstractmethod
    async def get_db_obj(
        self, *conditions: ColumnElement[bool], raise_exception: bool = False) -> T: ...

    @abstractmethod
    async def get_db_objs(
        self, *conditions: ColumnElement[bool]) -> list[T]: ...

    @abstractmethod
    async def get_column_vals(
        self, field: InstrumentedAttribute, *conditions: ColumnElement[bool]) -> list: ...

    @abstractmethod
    async def get_columns_vals(self, fields: Sequence[InstrumentedAttribute],
                               *conditions: ColumnElement[bool], mapped: bool = False) -> list[tuple]: ...

    @abstractmethod
    async def delete_db_objs(
        self, *conditions: ColumnElement[bool]) -> list[T]: ...

    @abstractmethod
    async def update_db_objs(
        self, *conditions: ColumnElement[bool], **kwargs) -> list[T]: ...

    @abstractmethod
    async def create_db_obj(self, **kwargs) -> T: ...

    @abstractmethod
    async def create_db_objs(self, table_raws: Sequence[dict]) -> list[T]: ...

    async def force_commit(self):
        await self.session.commit()

    async def refresh(self, obj: T):
        await self.session.refresh(obj)


class DBSocket(Socket):
    async def get_db_obj(self, *conditions: ColumnElement[bool], raise_exception: bool = False) -> T:
        query = select(self.model).where(*conditions)
        db_resp = await self.session.execute(query)
        if raise_exception:
            return db_resp.scalar_one()
        return db_resp.scalar_one_or_none()

    async def get_db_objs(self, *conditions: ColumnElement[bool]) -> list[T]:
        query = select(self.model).where(*conditions)
        db_resp = await self.session.execute(query)
        return db_resp.scalars().all()

    async def get_column_vals(self, field: InstrumentedAttribute, *conditions: ColumnElement[bool]) -> list:
        query = select(field).where(*conditions)
        db_resp = await self.session.execute(query)
        return db_resp.scalars().all()

    async def get_columns_vals(self, fields: Sequence[InstrumentedAttribute], *conditions: ColumnElement[bool], mapped: bool = False) -> list[tuple]:
        assert len(fields) >= 2, 'Minimal count of fields - 2'
        query = select(*fields).where(*conditions)
        db_resp = await self.session.execute(query)
        if mapped:
            res = db_resp.mappings().all()
        else:
            res = db_resp.all()
        return res

    @commitable
    async def delete_db_objs(self, *conditions: ColumnElement[bool]) -> list[T]:
        """commitable method"""
        query = delete(self.model).where(*conditions).returning(self.model)
        res = await self.session.execute(query)
        return res.scalars().all()

    @commitable
    async def update_db_objs(self, *conditions: ColumnElement[bool], **kwargs) -> list[T]:
        """commitable method"""
        query = update(self.model).where(
            *conditions).values(**kwargs).returning(self.model)
        res = await self.session.execute(query)
        updated = res.scalars().all()
        return updated

    @commitable
    async def create_db_obj(self, **kwargs) -> T:
        """commitable method"""
        query = insert(self.model).values(**kwargs).returning(self.model)
        res = await self.session.execute(query)
        obj = res.scalar_one()
        return obj

    @commitable
    async def create_db_objs(self, table_raws: Sequence[dict]) -> list[T]:
        """commitable method"""
        query = insert(self.model).values(table_raws).returning(self.model)
        res = await self.session.execute(query)
        objs = res.scalars().all()
        return objs


class SocketFactory:
    @classmethod
    def get_socket(cls, model: T, session: AsyncSession):
        return DBSocket(model, session)
