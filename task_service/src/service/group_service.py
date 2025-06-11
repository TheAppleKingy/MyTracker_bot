from typing import Sequence

from sqlalchemy.sql.expression import ColumnElement
from sqlalchemy.orm.attributes import InstrumentedAttribute

from models.users import User, Group
from .abstract import Service


class GroupService(Service):
    _target_model = Group

    async def get_group(self, *conditions: ColumnElement[bool], raise_exception: bool = False) -> Group:
        user = await self.socket.get_db_obj(*conditions, raise_exception=raise_exception)
        return user

    async def get_groups(self, *conditions: ColumnElement[bool]) -> list[Group]:
        users = await self.socket.get_db_objs(*conditions)
        return users

    async def get_column_vals(self, field: InstrumentedAttribute, *conditions: ColumnElement[bool]) -> list:
        data = await self.socket.get_column_vals(field, *conditions)
        return data

    async def get_columns_vals(self, fields: Sequence[InstrumentedAttribute], *conditions: ColumnElement[bool], mapped: bool = False) -> list[tuple]:
        data = await self.socket.get_columns_vals(fields, *conditions, mapped)
        return data

    async def delete_group(self, *conditions: ColumnElement[bool]) -> list[Group]:
        deleted = await self.socket.delete_db_objs(*conditions)
        return deleted

    async def update_groups(self, *conditions: ColumnElement[bool], **kwargs) -> list[Group]:
        updated = await self.socket.update_db_objs(*conditions, **kwargs)
        return updated

    async def create_group(self, **kwargs) -> Group:
        created = await self.socket.create_db_obj(**kwargs)
        return created

    async def create_group(self, table_raws: Sequence[dict]) -> list[Group]:
        created = await self.socket.create_db_objs(table_raws)
        return created

    async def add_users(self, group: Group, users: Sequence[User]) -> list[User]:
        to_add = []
        for user in users:
            if user not in group.users:
                group.users.append(user)
                to_add.append(user)
        await self.socket.force_commit()
        return to_add

    async def exclude_users(self, group: Group, users: Sequence[User]) -> list[User]:
        excluded = []
        for user in users:
            if user in group.users:
                idx = group.users.index(user)
                deleted_user = group.users.pop(idx)
                excluded.append(user)
        await self.socket.force_commit()
        return deleted_user
