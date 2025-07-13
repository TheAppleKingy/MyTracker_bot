from typing import Optional
from datetime import datetime, timezone, timedelta

from pydantic import BaseModel, Field


class TaskSchema(BaseModel):
    def show_to_message(self, user_tz: timezone, exclude: list[str]):
        view = ''
        black_list = ['subtasks', 'id']
        for field_name in self.__class__.model_fields:
            if (not field_name in exclude):
                val = getattr(self, field_name, None)
                if isinstance(val, datetime):
                    dt = val.astimezone(user_tz)
                    val = dt.strftime('%d.%m.%Y at %H:%M')
                view += field_name.capitalize().replace('_', ' ')+f': {val}\n'
        view += 'Subtasks:'
        return view


class TaskCreatedSchema(TaskSchema):
    id: int
    title: str = Field(max_length=100)
    description: str = Field(max_length=500)
    creation_date: datetime
    deadline: datetime
    task_id: Optional[int] = None

    def show_to_message(self, user_tz: timezone, exclude: list[str] = ['task_id', 'id', 'subtasks']):
        return super().show_to_message(user_tz, exclude)


class TaskViewSchema(TaskSchema):
    id: int
    title: str
    description: str
    creation_date: datetime
    deadline: datetime
    pass_date: Optional[datetime]
    done: bool
    subtasks: list['TaskViewSchema']

    def show_to_message(self, user_tz: timezone, exclude: list[str] = ['id', 'subtasks']):
        return super().show_to_message(user_tz, exclude)
