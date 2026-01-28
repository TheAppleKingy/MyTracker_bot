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
    creation_time: Optional[datetime] = None
    pass_date: Optional[datetime] = None
    subtasks: list["Task"] = field(default_factory=list)
