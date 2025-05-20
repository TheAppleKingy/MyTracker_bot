from models.models import User

from fastapi import HTTPException, status


class IsAdmin:
    def __init__(self, user: User):
        self.__user = user

    def is_user_allowed(self) -> bool:
        pass


class PermissionFactory:
    permission_classes = [IsAdmin, ]

    def get_permission(self, perm_alias: str):
        for perm in self.permission_classes:
            if perm_alias == perm.__name__.lower():
                pass

    def get_allowed_user():
        pass
