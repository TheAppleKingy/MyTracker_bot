from datetime import datetime, timezone, timedelta

from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.orm import relationship, mapped_column, validates, Mapped

from .associations import Base


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
    done: Mapped[bool] = mapped_column(default=False)
    subtasks: Mapped[list['SubTask']] = relationship(
        back_populates='task', cascade='all, delete-orphan', lazy='selectin')
    user: Mapped['User'] = relationship(
        back_populates='tasks', lazy='selectin')
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))

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
    done: Mapped[bool] = mapped_column(default=False)
    task: Mapped["Task"] = relationship(
        back_populates='subtasks', lazy='selectin')
    task_id: Mapped[int] = mapped_column(ForeignKey('tasks.id'))

    @validates('pass_date')
    def validate_pass_date(self, key, value):
        if (value is not None) and (self.creation_date is not None) and (value < self.creation_date):
            raise ValueError("Pass date cannot be less than creation date")
        return value
