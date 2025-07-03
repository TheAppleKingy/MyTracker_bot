from fastapi import Depends, Cookie
from sqlalchemy.ext.asyncio import AsyncSession

from infra.db.session import get_db_session
from infra.db.repository.user_repo import UserRepository
from infra.db.repository.task_repo import TaskRepository
from infra.db.repository.group_repo import GroupRepository
from infra.db.repository.factories import UserRepoFactory, TaskRepoFactory, GroupRepositoryFactory
from infra.db.models.users import User
from service.factories import UserServiceFactory, GroupServiceFactory, TaskServiceFactory
from service.user_service import UserService, UserAuthService, UserPermissionService


def get_user_repo(session: AsyncSession = Depends(get_db_session)):
    return UserRepoFactory.get_user_repository(session)


def get_task_repo(session: AsyncSession = Depends(get_db_session)):
    return TaskRepoFactory.get_task_repository(session)


def get_group_repo(session: AsyncSession = Depends(get_db_session)):
    return GroupRepositoryFactory.get_group_repository(session)


def get_user_service(user_repo: UserRepository = Depends(get_user_repo), task_repo: TaskRepository = Depends(get_task_repo)):
    return UserServiceFactory.get_service(user_repo, task_repo)


def get_user_auth_service(user_repo: UserRepository = Depends(get_user_repo)):
    return UserServiceFactory.get_auth_service(user_repo)


def get_perm_service_for(allowed_group_name: str):
    def get_user_perm_service(user_repo: UserRepository = Depends(get_user_repo)):
        return UserServiceFactory.get_permission_service(user_repo, allowed_group_name)
    return get_user_perm_service


def get_task_service(task_repo: TaskRepository = Depends(get_task_repo), user_repo: UserRepository = Depends(get_user_repo)):
    return TaskServiceFactory.get_service(task_repo, user_repo)


def get_group_service(group_repo: GroupRepository = Depends(get_group_repo), user_repo: UserRepository = Depends(get_user_repo)):
    return GroupServiceFactory.get_service(group_repo, user_repo)


async def authenticate(token: str = Cookie(default=None, include_in_schema=False), auth_service: UserAuthService = Depends(get_user_auth_service)):
    return await auth_service.auth_user(token)


def get_user_allowed_by_group(allowed_group: str):
    async def check_user(user: User = Depends(authenticate), perm_service: UserPermissionService = Depends(get_perm_service_for(allowed_group))):
        return perm_service.check(user.id)
    return check_user


async def for_admin_only(user: User = Depends(authenticate), perm_service: UserPermissionService = Depends(get_perm_service_for('Admin'))):
    return await perm_service.check(user.id)
