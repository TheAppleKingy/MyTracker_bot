from typing import Optional
from datetime import datetime

from pydantic import BaseModel, field_validator


class Task(BaseModel):
    id: int
    title: str
    description: str
    creation_date: datetime
    deadline: datetime
    pass_date: Optional[datetime]
    done: bool
    subtasks: list['Task']

    def __str__(self):
        pass_date = '-'
        if self.pass_date:
            pass_date = self.pass_date.strftime('%d.%m.%Y at %H:%M')
        return f'Title: {self.title}\nDescription: {self.description}\nCreation date: {self.creation_date.strftime('%d.%m.%Y at %H:%M')}\nDeadline: {self.deadline.strftime('%d.%m.%Y at %H:%M')}\nPass date: {pass_date}\nDone: {self.done}\nSubtasks:'
