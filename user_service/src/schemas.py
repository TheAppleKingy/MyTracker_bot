from pydantic import BaseModel, Field


class UserCreateSchema(BaseModel):
    username: str = Field(max_length=256)
    email: str = Field(max_length=256)
    password: str = Field(max_length=25)


class UserViewSchema(BaseModel):
    username: str
    email: str

    class Config:
        orm_mode = True
