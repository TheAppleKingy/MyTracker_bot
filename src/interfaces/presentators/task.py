from datetime import datetime, timezone
from dataclasses import fields

from src.domain.entities import Task
from src.logger import logger


def show_task_data(task: Task, user_tz: timezone, exclude: list[str] = ["id", "subtasks", "parent_id"]):
    view = ''
    for field in fields(task):
        if (not field.name in exclude):
            val = getattr(task, field.name, None)
            logger.critical(f"val dt is {val} name f {field.name} type {type(val)}")
            if field.name == 'pass_date' and not val:
                continue
            if isinstance(val, datetime):
                logger.critical(f"val dt is {val} name f {field.name}")
                dt = val.astimezone(user_tz)
                val = dt.strftime('%d.%m.%Y at %H:%M')
            view += "<b>"+field.name.capitalize().replace('_', ' ') + "</b>" + \
                f': {val}\n--------------\n'
    return view
