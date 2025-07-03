from sqlalchemy.ext.asyncio import AsyncSession

from ..models.users import User, Group
from ..models.tasks import Task
from .base import T
from .user_repo import UserRepository
from .task_repo import TaskRepository
from .group_repo import GroupRepository
from .base import BaseRepo


class BaseRepoFactory:
    @classmethod
    def get_repository(cls, model: T, session: AsyncSession):
        return BaseRepo(model, session)


class UserRepoFactory:
    @classmethod
    def get_user_repository(cls, session: AsyncSession):
        repo = BaseRepoFactory.get_repository(User, session)
        return UserRepository(repo)


class TaskRepoFactory:
    @classmethod
    def get_task_repository(cls, session: AsyncSession):
        repo = BaseRepoFactory.get_repository(Task, session)
        return TaskRepository(repo)


class GroupRepositoryFactory:
    @classmethod
    def get_group_repository(cls, session: AsyncSession):
        repo = BaseRepoFactory.get_repository(Group, session)
        return GroupRepository(repo)
