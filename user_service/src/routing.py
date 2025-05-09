from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from schemas import UserCreateSchema, UserViewSchema

from database import get_db_session

from models.models import User

from typing import List

user_router = APIRouter(
    prefix='/users',
    tags=['Users']
)


@user_router.post('')
async def create_user(user_data: UserCreateSchema, session: AsyncSession = Depends(get_db_session)):
    user = User(username=user_data.username, password=user_data.password)
    user.set_password()
    session.add(user)
    await session.commit()

    return {'detail': 'ok'}


@user_router.get('', response_model=List[UserViewSchema])
async def get_users(session: AsyncSession = Depends(get_db_session)):
    query = await session.execute(select(User))
    users = query.scalars().all()
    return users
