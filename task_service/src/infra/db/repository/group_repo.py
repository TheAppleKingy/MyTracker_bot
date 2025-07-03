from typing import Sequence

from sqlalchemy.orm import selectinload

from ..models.users import User, Group
from .base import InitRepo


class GroupRepository(InitRepo):
    _model = Group

    async def get_group(self, id: int) -> Group | None:
        return await self._repo.get_db_obj(Group.id == id)

    async def get_all_groups(self) -> list[Group]:
        return await self._repo.get_db_objs(options=[selectinload(Group.users)])

    async def get_group_and_users(self, id: int) -> Group | None:
        return await self._repo.get_db_obj(Group.id == id, options=[selectinload(Group.users)])

    async def add_users_in_group(self, group_id: int, users: Sequence[User]) -> list[User]:
        group = await self.get_group_and_users(group_id)
        added = []
        for user in users:
            if not user in group.users:
                group.users.append(user)
                added.append(user)
        await self._repo.force_commit()
        return added

    async def exclude_users_from_group(self, group_id: int, users: Sequence[User]) -> list[User]:
        group = await self.get_group_and_users(group_id)
        excluded = []
        for user in users:
            if user in group.users:
                idx = group.users.index(user)
                del group.users[idx]
                excluded.append(user)
        await self._repo.force_commit()
        return excluded
