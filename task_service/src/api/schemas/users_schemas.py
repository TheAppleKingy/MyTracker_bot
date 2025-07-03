from typing import Optional

from pydantic import BaseModel, Field


class UserCreateSchema(BaseModel):
    tg_name: str = Field(max_length=50)
    email: str = Field(max_length=50)
    first_name: Optional[str] = Field(max_length=100, default=None)
    last_name: Optional[str] = Field(max_length=100, default=None)
    password: str = Field(max_length=25)


class UserViewSchema(BaseModel):
    id: Optional[int] = Field(default=None)
    tg_name: Optional[str] = Field(default=None)
    email: Optional[str] = Field(default=None)


class UserUpdateSchema(BaseModel):
    tg_name: Optional[str] = Field(max_length=50, default=None)
    email: Optional[str] = Field(max_length=50, default=None)
    first_name: Optional[str] = Field(max_length=100, default=None)
    last_name: Optional[str] = Field(max_length=100, default=None)
    is_active: Optional[bool] = None


class LoginSchema(BaseModel):
    email: str
    password: str


class UserInGroupSchema(BaseModel):
    id: int
