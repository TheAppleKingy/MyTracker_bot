from pydantic import BaseModel, Field

from .users_schemas import UserViewSchema, UserInGroupSchema


class GroupVeiwSchema(BaseModel):
    id: int
    title: str = Field(max_length=20)
    users: list[UserViewSchema]

    class Config:
        orm_mode = True


class GroupUpdateSchema(BaseModel):
    users: list[UserInGroupSchema]
