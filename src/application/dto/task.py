from typing import Optional
from datetime import datetime

from pydantic import BaseModel


class TaskViewSchema(BaseModel):
    id: int
    title: str
    description: str
    creation_date: datetime
    deadline: datetime
    pass_date: Optional[datetime] = None
    parent_id: Optional[int] = None
    subtasks: list["TaskPreviewDTO"] = []


class TaskPreviewDTO(BaseModel):
    id: int
    title: str
