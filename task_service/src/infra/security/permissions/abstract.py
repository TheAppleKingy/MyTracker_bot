from abc import ABC, abstractmethod

from infra.db.models.users import User


class AbstractPermission(ABC):
    """interface for classes defining permission control"""
    @abstractmethod
    def check_user(self, user: User) -> None:
        """if user has no permission exc PermissionException must be raised"""
        ...
