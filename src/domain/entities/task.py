from dataclasses import dataclass, field, fields
from datetime import datetime, timezone
from typing import Optional


@dataclass
class Task:
    title: str
    deadline: datetime
    id: int = None
    description: Optional[str] = None
    parent_id: Optional[int] = None
    creation_date: Optional[datetime] = None
    pass_date: Optional[datetime] = None
    subtasks: list["Subtask"] = field(default_factory=list)


@dataclass
class Subtask:
    id: int
    title: str
