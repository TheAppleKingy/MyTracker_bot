from repository.socket import Socket
from .group_service import GroupService
from .user_service import UserService


class GroupServiceFactory:
    @classmethod
    def get_service(cls, socket: Socket):
        return GroupService(socket)


class UserServiceFactory:
    @classmethod
    def get_service(cls, socket: Socket):
        return UserService(socket)
