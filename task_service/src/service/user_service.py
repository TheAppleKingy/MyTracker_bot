from typing import Sequence

from sqlalchemy.sql.expression import ColumnElement
from sqlalchemy.orm.attributes import InstrumentedAttribute

from models.users import User
from security.password_utils import hash_password, check_password, is_hashed
from .abstract import Service


class UserService(Service):
    _target_model = User

    async def create_obj(self, commit: bool = True, **kwargs) -> User:
        raw_password = kwargs.pop('password')
        hashed = hash_password(raw_password)
        kwargs.setdefault('password', hashed)
        created = await super().create_obj(commit=commit, **kwargs)
        return created

    async def create_objs(self, table_raws: Sequence[dict], commit: bool = True) -> list[User]:
        for raw in table_raws:
            raw_password = raw.pop('password')
            hashed = hash_password(raw_password)
            raw.setdefault('password', hashed)
        created = await super().create_objs(table_raws, commit=commit)
        return created

    def check_password(self, user: User, password: str):
        hashed = is_hashed(user.password)
        if hashed:
            return check_password(password, user.password)
        return False

    async def set_password(self, user: User, password: str):
        user.password = hash_password(password)
        await self.socket.force_commit()
