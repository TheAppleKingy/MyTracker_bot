from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import JSONB

from security.password_utils import hash_password, check_password

from .associations import users_groups, Base


class User(Base):
    __tablename__ = 'users'
    tg_name: Mapped[str] = mapped_column(
        String(50), unique=True)
    email: Mapped[str] = mapped_column(
        String(50), unique=True)
    password: Mapped[str] = mapped_column()
    first_name: Mapped[str] = mapped_column(String(100), nullable=True)
    last_name: Mapped[str] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=False)
    groups: Mapped[list['Group']] = relationship(secondary=users_groups,
                                                 back_populates='users', lazy='selectin', passive_deletes=True)
    tasks: Mapped[list[int]] = mapped_column(JSONB, default=list)

    def set_password(self):
        self.password = hash_password(self.password)

    def check_password(self, verifiable: str):
        hashed_password = self.password
        return check_password(verifiable, hashed_password)


class Group(Base):
    __tablename__ = 'groups'
    title: Mapped[str] = mapped_column(String(20))
    users: Mapped[list['User']] = relationship(secondary=users_groups,
                                               back_populates='groups', lazy='selectin', passive_deletes=True)


"""By models/methods perms may be added"""
