from typing import Optional
from datetime import datetime, timezone

from pydantic import BaseModel


class TaskSchema(BaseModel):
    def show_to_message(self, user_tz: timezone, exclude: list[str]):
        view = ''
        for field_name in self.__class__.model_fields:
            if (not field_name in exclude):
                val = getattr(self, field_name, None)
                if field_name == 'pass_date' and not val:
                    continue
                if isinstance(val, datetime):
                    dt = val.astimezone(user_tz)
                    val = dt.strftime('%d.%m.%Y at %H:%M')
                view += "<b>"+field_name.capitalize().replace('_', ' ') + "</b>" + \
                    f': {val}\n--------------\n'
        view += '<b>Subtasks:</b>'
        return view


class TaskViewSchema(TaskSchema):
    id: Optional[int] = None
    title: str
    description: str
    creation_date: datetime
    deadline: datetime
    pass_date: Optional[datetime]
    task_id: Optional[int] = None
    subtasks: list['TaskViewSchema'] = []

    def show_to_message(self, user_tz: timezone, exclude: list[str] = ['id', 'subtasks', 'task_id']):
        return super().show_to_message(user_tz, exclude)
