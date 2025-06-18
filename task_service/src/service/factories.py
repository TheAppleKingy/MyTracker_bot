from repository.socket import Socket
from .group_service import GroupService
from .user_service import UserService
from .task_service import TaskService


class ServiceFactory:
    @classmethod
    def get_service(cls, socket: Socket): ...


class GroupServiceFactory(ServiceFactory):
    @classmethod
    def get_service(cls, socket: Socket):
        return GroupService(socket)


class UserServiceFactory(ServiceFactory):
    @classmethod
    def get_service(cls, socket: Socket):
        return UserService(socket)


class TaskServiceFactory(ServiceFactory):
    @classmethod
    def get_service(cls, socket: Socket):
        return TaskService(socket)
