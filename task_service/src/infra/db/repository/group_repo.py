from sqlalchemy import select
from sqlalchemy.orm import selectinload

from domain.entities.users import Group
from domain.repositories.group_repository import AbstractGroupRepository


class GroupRepository(AbstractGroupRepository):
    async def get_group(self, id: int) -> Group | None:
        return await self.session.get(Group, id)

    async def get_all_groups(self) -> list[Group]:
        db_resp = await self.session.scalars(select(Group).options(selectinload(Group.users)))
        return [g for g in db_resp.all()]

    async def get_group_and_users(self, id: int) -> Group | None:
        return await self.session.get(Group, id, options=[selectinload(Group.users)])

    async def commit(self):
        return await self.session.commit()
