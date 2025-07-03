from typing import Sequence

from infra.db.models.users import User, Group
from infra.db.repository.group_repo import GroupRepository
from infra.db.repository.user_repo import UserRepository
from .exceptions import GroupServiceException


class GroupService:
    def __init__(self, group_repository: GroupRepository, user_repository: UserRepository):
        self.repo = group_repository
        self.user_repo = user_repository

    async def get_groups_and_users(self):
        return await self.repo.get_all_groups()

    async def add_users(self, group_id: int, users_ids: Sequence[int]) -> list[User]:
        users = await self.user_repo.get_users_by(User.id.in_(users_ids))
        if len(users) != len(users_ids):
            got_ids = {user.id for user in users}
            not_existing = map(str, list(set(users_ids) - got_ids))
            raise GroupServiceException(
                f'"User" objects with next "id"s do not exist: {', '.join(not_existing)}')
        added = await self.repo.add_users_in_group(group_id, users)
        return added

    async def exclude_users(self, group_id: int, users_ids: Sequence[int]) -> list[User]:
        users = await self.user_repo.get_users_by(User.id.in_(users_ids))
        if len(users) != len(users_ids):
            got_ids = {user.id for user in users}
            not_existing = map(str, list(set(users_ids) - got_ids))
            raise GroupServiceException(
                f'"User" objects with next "id"s do not exist: {', '.join(not_existing)}')
        excluded = await self.repo.exclude_users_from_group(group_id, users)
        return excluded
