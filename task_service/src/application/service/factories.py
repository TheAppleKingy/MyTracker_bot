from domain.repositories.group_repository import AbstractGroupRepository
from domain.repositories.task_repository import AbstractTaskRepository
from domain.repositories.user_repository import AbstractUserRepository

from infra.security.permissions.abstract import AbstractPermission

from .group import GroupService
from .user import UserAuthService, UserPermissionService, UserAuthDataService
from .task import TaskService


class GroupServiceFactory:
    @classmethod
    def get_service(cls, group_repository: AbstractGroupRepository, user_repository: AbstractUserRepository):
        return GroupService(group_repository, user_repository)


class UserServiceFactory:
    @classmethod
    def get_auth_data_service(cls, user_repository: AbstractUserRepository):
        return UserAuthDataService(user_repository)

    @classmethod
    def get_auth_service(cls, user_repository: AbstractUserRepository):
        return UserAuthService(user_repository)

    @classmethod
    def get_permission_service(cls, permission_objs: list[AbstractPermission]):
        return UserPermissionService(permission_objs)


class TaskServiceFactory:
    @classmethod
    def get_service(cls, task_repository: AbstractTaskRepository, user_repository: AbstractUserRepository):
        return TaskService(task_repository, user_repository)
