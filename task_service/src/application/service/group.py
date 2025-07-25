from typing import Sequence

from domain.entities.users import User
from domain.repositories.group_repository import AbstractGroupRepository
from domain.repositories.user_repository import AbstractUserRepository
from .exceptions import GroupServiceError


class GroupService:
    def __init__(self, group_repository: AbstractGroupRepository, user_repository: AbstractUserRepository):
        self.repo = group_repository
        self.user_repo = user_repository

    async def get_groups_and_users(self):
        return await self.repo.get_all_groups()

    async def add_users(self, group_id: int, users_ids: Sequence[int]) -> list[User]:
        users = await self.user_repo.get_users_by(User.id.in_(users_ids))
        if len(users) != len(users_ids):
            got_ids = {user.id for user in users}
            not_existing = map(str, list(set(users_ids) - got_ids))
            raise GroupServiceError(
                f'"User" objects with next "id"s do not exist: {', '.join(not_existing)}')
        group = await self.repo.get_group(group_id)
        if not group:
            raise GroupServiceError(
                'Group with provided id does not exist')
        added = group.add_users(users)
        await self.repo.commit()
        return added

    async def exclude_users(self, group_id: int, users_ids: Sequence[int]) -> list[User]:
        users = await self.user_repo.get_users_by(User.id.in_(users_ids))
        if len(users) != len(users_ids):
            got_ids = {user.id for user in users}
            not_existing = map(str, list(set(users_ids) - got_ids))
            raise GroupServiceError(
                f'"User" objects with next "id"s do not exist: {', '.join(not_existing)}')
        group = await self.repo.get_group(group_id)
        if not group:
            raise GroupServiceError(
                'Group with provided id does not exist')
        excluded = group.exclude_users(users)
        await self.repo.commit()
        return excluded
