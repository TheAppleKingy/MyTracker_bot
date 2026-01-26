from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Task:
    title: str
    id: int = None
    deadline: datetime
    description: Optional[str] = None
    parent_id: Optional[int] = None
    creation_time: Optional[datetime] = None
    pass_date: Optional[datetime] = None
    subtasks: list["Task"] = field(default_factory=list)
