from abc import ABC, abstractmethod

from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities.users import Group


class AbstractGroupRepository(ABC):
    def __init__(self, session: AsyncSession):
        self.session = session

    @abstractmethod
    async def get_group(self, id: int) -> Group | None: ...

    @abstractmethod
    async def get_all_groups(self) -> list[Group]: ...

    @abstractmethod
    async def get_group_and_users(self, id: int) -> Group | None: ...

    @abstractmethod
    async def commit(self) -> None: ...
