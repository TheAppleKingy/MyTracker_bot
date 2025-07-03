from sqlalchemy.sql.expression import ColumnElement
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from infra.exc import parse_integrity_err_msg
from ..models.users import User
from ..models.tasks import Task
from .base import InitRepo
from .exceptions import UserRepositoryError


class UserRepository(InitRepo):
    _model = User

    async def get_user(self, id: int) -> User | None:
        return await self._repo.get_db_obj(User.id == id)

    async def get_user_by_email(self, email: str) -> User | None:
        return await self._repo.get_db_obj(User.email == email)

    async def get_user_and_groups(self, id: int) -> User | None:
        return await self._repo.get_db_obj(User.id == id, options=[selectinload(User.groups)])

    async def get_user_and_tasks(self, id: int) -> User | None:
        return await self._repo.get_db_obj(User.id == id, options=[selectinload(User.tasks)])

    async def get_users_by(self, *conditions: ColumnElement[bool]) -> list[User]:
        return await self._repo.get_db_objs(*conditions)

    async def create_user(self, **user_data: dict) -> User:
        try:
            return await self._repo.create_db_obj(**user_data)
        except SQLAlchemyError as e:
            if isinstance(e, IntegrityError):
                msg = parse_integrity_err_msg(str(e))
            raise UserRepositoryError(msg, e)

    async def delete_user(self, id: int) -> User:
        return await self._repo.delete_db_objs(User.id == id)

    async def update_user(self, id: int, **kwargs) -> User:
        return await self._repo.update_db_objs(User.id == id, **kwargs)
