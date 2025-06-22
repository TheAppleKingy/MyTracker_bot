from typing import Sequence

from models.users import User, Group
from .abstract import Service, add_related_objs, exclude_related_objs


class GroupService(Service[Group]):
    _target_model = Group

    async def add_users(self, group: Group, users: Sequence[User]) -> list[User]:
        added = add_related_objs(group, users, Group.users)
        await self.socket.force_commit()
        return added

    async def exclude_users(self, group: Group, users: Sequence[User]) -> list[User]:
        excluded = exclude_related_objs(group, users, Group.users)
        await self.socket.force_commit()
        return excluded
