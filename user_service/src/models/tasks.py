from .users import User

from . import Base

from datetime import datetime, timezone, timedelta

from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from sqlalchemy import String, Table, Column, ForeignKey, DateTime, func, Boolean


users_tasks = Table(
    'users_tasks',
    Base.metadata,
    Column('user_id', ForeignKey('users.id'), primary_key=True),
    Column('task_id', ForeignKey('tasks.id'), primary_key=True)
)


class Task(Base):
    __tablename__ = 'tasks'
    title: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(unique=True)
    creation_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.now(tz=timezone.utc))
    deadline: Mapped[datetime] = mapped_column(DateTime(
        timezone=True), default=datetime.now(tz=timezone.utc)+timedelta(days=7))
    pass_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True)
    done: Mapped[bool] = mapped_column(Boolean, default=False)
    subtasks: Mapped[list['SubTask']] = relationship(
        back_populates='task', cascade='all, delete-orphan', lazy='joined')
    users: Mapped[list['User']] = relationship(
        secondary=users_tasks, back_populates='tasks', lazy='joined')

    @validates('pass_date')
    def validate_pass_date(self, key, value):
        if (value is not None) and (self.creation_date is not None) and (value < self.creation_date):
            raise ValueError("Pass date cannot be less than creation date")
        return value


class SubTask(Base):
    __tablename__ = 'subtasks'
    title: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(unique=True)
    creation_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.now(tz=timezone.utc))
    deadline: Mapped[datetime] = mapped_column(DateTime(
        timezone=True), default=datetime.now(tz=timezone.utc)+timedelta(days=7))
    pass_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True)
    done: Mapped[bool] = mapped_column(Boolean, default=False)
    task: Mapped["Task"] = relationship(
        back_populates='subtasks', lazy='joined')
    task_id: Mapped[int] = mapped_column(ForeignKey('tasks.id'))

    @validates('pass_date')
    def validate_pass_date(self, key, value):
        if (value is not None) and (self.creation_date is not None) and (value < self.creation_date):
            raise ValueError("Pass date cannot be less than creation date")
        return value
