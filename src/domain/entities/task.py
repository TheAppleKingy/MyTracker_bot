from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Task:
    title: str
    deadline: datetime
    id: int = None  # type: ignore
    description: Optional[str] = None
    parent_id: Optional[int] = None
    creation_date: Optional[datetime] = None
    pass_date: Optional[datetime] = None


@dataclass
class TaskPreview:
    id: int
    title: str
    parent_id: Optional[int] = None
