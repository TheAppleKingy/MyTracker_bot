from . import Base

from .tasks import Task, users_tasks

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Table, Column, ForeignKey

from security import hash_password, check_password


users_groups = Table(
    'users_groups',
    Base.metadata,
    Column('user_id', ForeignKey('users.id'), primary_key=True),
    Column('group_id', ForeignKey('groups.id'), primary_key=True)
)


class User(Base):
    __tablename__ = 'users'
    username: Mapped[str] = mapped_column(
        String(50), unique=True)
    email: Mapped[str] = mapped_column(
        String(50), unique=True)
    password: Mapped[str] = mapped_column()
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    is_active: Mapped[bool] = mapped_column(default=False)
    groups = relationship(secondary=users_groups,
                          back_populates='users')
    tasks: Mapped[list['Task']] = relationship(
        secondary=users_tasks, back_populates='users', lazy='joined')

    def set_password(self):
        self.password = hash_password(self.password)

    def check_password(self, verifiable: str):
        hashed_password = self.password
        return check_password(verifiable, hashed_password)


class Group(Base):
    __tablename__ = 'groups'
    title: Mapped[str] = mapped_column(String(20), nullable=False)
    users = relationship('User', secondary=users_groups,
                         back_populates='groups', lazy='joined')


"""By models/methods perms may be added"""
