from typing import Sequence

from sqlalchemy.sql.expression import ColumnElement
from sqlalchemy.orm.attributes import InstrumentedAttribute

from .abstract import Service

from models.models import User


class UserService(Service):
    _target_model = User

    async def get_user(self, *conditions: ColumnElement[bool], raise_exception: bool = False) -> User:
        user = await self.socket.get_db_obj(*conditions, raise_exception=raise_exception)
        return user

    async def get_users(self, *conditions: ColumnElement[bool]) -> list[User]:
        users = await self.socket.get_db_objs(*conditions)
        return users

    async def get_column_vals(self, field: InstrumentedAttribute, *conditions: ColumnElement[bool]) -> list:
        data = await self.socket.get_column_vals(field, *conditions)
        return data

    async def get_columns_vals(self, fields: Sequence[InstrumentedAttribute], *conditions: ColumnElement[bool], mapped: bool = False) -> list[tuple]:
        data = await self.socket.get_columns_vals(fields, *conditions, mapped)
        return data

    async def delete_users(self, *conditions: ColumnElement[bool]) -> list[User]:
        deleted = await self.socket.delete_db_objs(*conditions)
        return deleted

    async def update_users(self, *conditions: ColumnElement[bool], **kwargs) -> list[User]:
        updated = await self.socket.update_db_objs(*conditions, **kwargs)
        return updated

    async def create_user(self, **kwargs) -> User:
        created = await self.socket.create_db_obj(**kwargs)
        return created

    async def create_users(self, table_raws: Sequence[dict]) -> list[User]:
        created = await self.socket.create_db_objs(table_raws)
        return created
