from typing import Optional
from datetime import datetime, timezone

from pydantic import BaseModel


class TaskSchema(BaseModel):
    def show_to_message(self, user_tz: timezone, exclude: list[str]):
        view = ''
        for field_name in self.__class__.model_fields:
            if (not field_name in exclude):
                val = getattr(self, field_name, None)
                if isinstance(val, datetime):
                    dt = val.astimezone(user_tz)
                    val = dt.strftime('%d.%m.%Y at %H:%M')
                view += field_name.capitalize().replace('_', ' ') + \
                    f': {val}\n--------------\n'
        view += 'Subtasks:'
        return view


class TaskViewSchema(TaskSchema):
    id: Optional[int] = None
    title: str
    description: str
    creation_date: datetime
    deadline: datetime
    pass_date: Optional[datetime]
    done: Optional[bool]
    task_id: Optional[int] = None
    subtasks: list['TaskViewSchema'] = []

    def show_to_message(self, user_tz: timezone, exclude: list[str] = ['id', 'subtasks', 'task_id']):
        return super().show_to_message(user_tz, exclude)
