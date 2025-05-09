from pydantic import BaseModel, Field


class UserCreateSchema(BaseModel):
    username: str = Field(max_length=256)
    password: str = Field(max_length=25)


class UserViewSchema(BaseModel):
    username: str

    class Config:
        orm_mode = True
