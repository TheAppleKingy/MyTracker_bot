from datetime import datetime, timezone
from dataclasses import fields

from src.domain.entities import Task


def show_task_data(task: Task, user_tz: timezone, exclude: list[str] = ["id", "subtasks", "parent_id"]):
    view = ''
    for field in fields(task):
        if (not field.name in exclude):
            val = getattr(task, field.name, None)
            if field.name == 'pass_date' and not val:
                continue
            if isinstance(val, datetime):
                dt = val.astimezone(user_tz)
                val = dt.strftime('%d.%m.%Y at %H:%M')
            view += "<b>"+field.name.capitalize().replace('_', ' ') + "</b>" + \
                f': {val}\n--------------\n'
    view += '<b>Subtasks:</b>'
    return view
