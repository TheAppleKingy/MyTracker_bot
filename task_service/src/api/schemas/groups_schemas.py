from pydantic import BaseModel, Field, field_validator

from .users_schemas import UserViewSchema


class GroupVeiwSchema(BaseModel):
    id: int
    title: str = Field(max_length=20)
    users: list[UserViewSchema]

    class Config:
        orm_mode = True


class GroupUpdateSchema(BaseModel):
    users: list[int]

    @field_validator('users')
    def validate_users(cls, val):
        return list(set(val))
