from infra.db.repository.user_repo import UserRepository
from infra.db.repository.task_repo import TaskRepository
from infra.db.repository.group_repo import GroupRepository

from .group_service import GroupService
from .user_service import UserService, UserAuthService, UserPermissionService
from .task_service import TaskService


class GroupServiceFactory:
    @classmethod
    def get_service(cls, group_repository: GroupRepository, user_repository: UserRepository):
        return GroupService(group_repository, user_repository)


class UserServiceFactory:
    @classmethod
    def get_service(cls, user_repository: UserRepository, task_repository: TaskRepository):
        return UserService(user_repository, task_repository)

    @classmethod
    def get_auth_service(cls, user_repository: UserRepository):
        return UserAuthService(user_repository)

    @classmethod
    def get_permission_service(cls, user_repository: UserRepository, allowed_group: str):
        return UserPermissionService(user_repository, allowed_group)


class TaskServiceFactory:
    @classmethod
    def get_service(cls, task_repository: TaskRepository, user_repository: UserRepository):
        return TaskService(task_repository, user_repository)
