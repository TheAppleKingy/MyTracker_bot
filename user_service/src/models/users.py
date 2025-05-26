from . import Base

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
        String(50), nullable=False, unique=True)
    email: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    is_active = Mapped[bool] = mapped_column(nullable=False, default=False)
    groups = relationship('Group', secondary=users_groups,
                          back_populates='users')

    def set_password(self):
        self.password = hash_password(self.password)

    def check_password(self, verifiable: str):
        hashed_password = self.password
        return check_password(verifiable, hashed_password)


class Group(Base):
    __tablename__ = 'groups'
    title: Mapped[str] = mapped_column(String(20), nullable=False)
    users = relationship('User', secondary=users_groups,
                         back_populates='groups')


"""By models/methods perms may be added"""
