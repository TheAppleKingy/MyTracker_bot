from typing import Sequence

from sqlalchemy.sql.expression import ColumnElement
from sqlalchemy.orm.attributes import InstrumentedAttribute

from models.users import User, Group
from .abstract import Service


class GroupService(Service):
    _target_model = Group

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
                excluded.append(deleted_user)
        await self.socket.force_commit()
        return excluded
