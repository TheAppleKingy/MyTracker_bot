from datetime import datetime, timezone, timedelta

from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.orm import relationship, mapped_column, validates, Mapped

from .associations import Base


class Task(Base):
    __tablename__ = 'tasks'
    title: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(String(500))
    creation_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.now(tz=timezone.utc))
    deadline: Mapped[datetime] = mapped_column(DateTime(
        timezone=True), default=datetime.now(tz=timezone.utc)+timedelta(days=7))
    pass_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None)
    done: Mapped[bool] = mapped_column(default=False)
    user: Mapped['User'] = relationship(
        back_populates='tasks', lazy='selectin')
    user_id: Mapped[int] = mapped_column(ForeignKey(
        'users.id', ondelete='CASCADE'), index=True)
    task_id: Mapped[int | None] = mapped_column(
        ForeignKey('tasks.id', ondelete='CASCADE'), nullable=True, index=True)
    task: Mapped['Task'] = relationship(
        remote_side='Task.id', back_populates='subtasks', lazy='selectin')
    subtasks: Mapped[list['Task']] = relationship(
        back_populates='task', cascade='all, delete-orphan', lazy='selectin')

    @validates('pass_date')
    def validate_pass_date(self, key, value):
        if (value is not None) and (self.creation_date is not None) and (value < self.creation_date):
            raise ValueError("Pass date cannot be less than creation date")
        return value

    @validates('done')
    def validate_done(self, key, value):
        if value and not self.pass_date:
            raise ValueError(
                f'Have to set pass_date before setting "task.done" to True in Task obj "{self.title}"')
        return value
