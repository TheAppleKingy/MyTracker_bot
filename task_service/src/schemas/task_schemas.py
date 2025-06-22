from typing import Optional
from datetime import datetime

from pydantic import BaseModel, Field
from .users_schemas import UserViewSchema


class TaskCreateSchema(BaseModel):
    title: str = Field(max_length=100)
    description: str = Field(max_length=500)
    deadline: Optional[datetime] = None
    user_id: int


class TaskViewSchema(BaseModel):
    id: int
    title: str
    description: str
    creation_date: datetime
    deadline: datetime
    pass_date: Optional[datetime]
    done: bool
    user: UserViewSchema
    task_id: Optional[int] = None


class TaskTreeSchema(TaskViewSchema):
    subtasks: list['TaskTreeSchema']


class TaskForUserSchema(BaseModel):
    id: int
    title: str
    description: str
    creation_date: datetime
    deadline: datetime
    pass_date: Optional[datetime]
    done: bool
    subtasks: list['TaskForUserSchema']

    class Config:
        orm_mode = True


class TaskUpdateSchema(BaseModel):
    title: Optional[str] = Field(max_length=100, default=None)
    description: Optional[str] = Field(max_length=500, default=None)
    deadline: Optional[datetime] = None
    pass_date: Optional[datetime] = None
    done: Optional[bool] = False
    user_id: Optional[int] = None


class TaskCreateForUserSchema(BaseModel):
    title: str = Field(max_length=100)
    description: str = Field(max_length=500)
    deadline: Optional[datetime] = None
    task_id: Optional[int] = None
