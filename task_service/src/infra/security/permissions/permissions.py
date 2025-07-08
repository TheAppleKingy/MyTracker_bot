from typing import Sequence

from infra.db.models.users import User
from infra.db.models.users import User
from .abstract import AbstractPermission
from .exc import PermissionException


class IsActivePermission(AbstractPermission):
    def check_user(self, user: User):
        if not user.is_active:
            raise PermissionException('User is not active')


class GroupPermission(AbstractPermission):
    def __init__(self, required_groups: Sequence[str]):
        self.required_groups = required_groups

    def check_user(self, user: User):
        user_groups = [group.title for group in user.groups]
        for group in self.required_groups:
            if not group in user_groups:
                raise PermissionException('User not in allowed group')
