from pydantic import BaseModel, Field, field_validator

from .users_dto import UserView


class GroupView(BaseModel):
    id: int
    title: str = Field(max_length=20)
    users: list[UserView]

    class Config:
        orm_mode = True


class GroupUpdate(BaseModel):
    users: list[int]

    @field_validator('users')
    def validate_users(cls, val):
        return list(set(val))
