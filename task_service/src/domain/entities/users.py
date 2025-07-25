from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infra.db.tables.associations import users_groups

from .tasks import Base


if TYPE_CHECKING:
    from .tasks import Task


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
    tasks: Mapped[list['Task']] = relationship(
        back_populates='user', cascade='all, delete-orphan', lazy='selectin')


class Group(Base):
    __tablename__ = 'groups'
    title: Mapped[str] = mapped_column(String(20))
    users: Mapped[list[User]] = relationship(secondary=users_groups,
                                             back_populates='groups', lazy='selectin', passive_deletes=True)

    def check_user_in(self, user: User):
        return user in self.users

    def add_users(self, users: list[User]) -> list[User]:
        added = []
        for user in users:
            if user not in self.users:
                self.users.append(user)
                added.append(user)
        return added

    def exclude_users(self, users: list[User]) -> list[User]:
        excluded = []
        for user in users:
            try:
                idx = self.users.index(user)
                del self.users[idx]
                excluded.append(user)
            except ValueError:
                continue
        return excluded


"""By models/methods perms may be added"""
