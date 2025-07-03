from typing import Callable, TypeVar, Sequence

from sqlalchemy import select, update, delete, insert
from sqlalchemy.sql.elements import TextClause
from sqlalchemy.orm import Load
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import ColumnElement
from sqlalchemy.orm.attributes import InstrumentedAttribute

from .exceptions import RepositoryError


T = TypeVar('T')


def commitable(commitable_method: Callable):
    """This decorator provides opportunity to commit changes in db after calling DBSocket methods. Changes will be commited by default. If don't need commit changes set "commit=False" """

    async def commit(self, *args, **kwargs):
        commit = kwargs.pop('commit', True)
        res = await commitable_method(self, *args, **kwargs)
        if commit:
            await self.force_commit()
        return res
    return commit


class BaseRepo:
    def __init__(self, model: T, session: AsyncSession):
        self.model = model
        self.session = session

    async def get_db_obj(self, *conditions: ColumnElement[bool], options: list[Load] = None) -> T | None:
        query = select(self.model).where(*conditions)
        if options:
            query = query.options(*options)
        db_resp = await self.session.execute(query)
        return db_resp.scalar_one_or_none()

    async def get_db_objs(self, *conditions: ColumnElement[bool], options: list[Load] = None) -> list[T]:
        query = select(self.model).where(*conditions)
        if options:
            query = query.options(*options)
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

    async def force_commit(self):
        await self.session.commit()

    async def refresh(self, obj: T, field_names: list[str] = None):
        await self.session.refresh(obj, attribute_names=field_names)

    async def execute_query(self, query: TextClause):
        return await self.session.execute(query)


class InitRepo:
    _model: T

    def __init__(self, repository: BaseRepo):
        if repository.model is not self._model:
            raise RepositoryError(
                f'Error init {self.__class__.__name__}: got BaseRepository where set model ({repository.model}), expected {self._model.__name__}', self.__class__.__name__)
        self._repo = repository
