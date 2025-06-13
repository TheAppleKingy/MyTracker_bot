import pytest
import httpx
import asyncio

from datetime import datetime, timedelta, timezone

from freezegun import freeze_time

from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from models.users import User
from models.associations import users_groups
from service.user_service import UserService
from schemas.users_schemas import UserViewSchema, UserUpdateSchema
from security.authentication import decode


pytest_mark_asyncio = pytest.mark.asyncio


@pytest_mark_asyncio
async def test_get_methods(user_service: UserService, session: AsyncSession, simple_user: User, admin_user: User):
    simple = await user_service.get_obj(User.tg_name == simple_user.tg_name)
    assert simple is not None
    with pytest.raises(NoResultFound):
        not_exist = await user_service.get_obj(User.tg_name == '[pas[o]]', raise_exception=True)
        assert not_exist is None

    users = await user_service.get_objs(User.tg_name.in_([simple_user.tg_name, admin_user.tg_name]))
    assert users != []
    assert len(users) == 2
    assert admin_user in users
    assert simple_user in users


@pytest_mark_asyncio
async def test_create_user(user_service: UserService, session: AsyncSession, simple_user: User, admin_user: User):
    data = {
        'tg_name': 'new_tg',
        'email': 'user@mail.ru',
        'password': 'test-password'
    }
    created = await user_service.create_obj(**data)
    assert created is not None
    query = select(User).where(User.tg_name == data['tg_name'])
    res = await session.execute(query)
    user = res.scalar_one_or_none()
    assert user is not None
    assert created == user
