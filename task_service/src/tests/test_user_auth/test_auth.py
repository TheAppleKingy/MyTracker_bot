import pytest
import httpx
import asyncio

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.users import User
from models.associations import users_groups
from service.user_service import UserService
from schemas.users_schemas import UserViewSchema, UserUpdateSchema


pytest_mark_asyncio = pytest.mark.asyncio


@pytest_mark_asyncio
async def test_registration(simple_client: httpx.AsyncClient, user_service: UserService):
    data = {
        'tg_name': 'new_tg',
        'email': 'user@mail.ru',
        'password': 'test-password'
    }
    response = await simple_client.post('/api/profile/registration', json=data)
    assert response.status_code == 200
    registered = await user_service.get_user(User.tg_name == data['tg_name'])
    assert registered is not None
    expected = UserViewSchema.model_validate(
        registered, from_attributes=True).model_dump()
    assert response.json() == expected


@pytest_mark_asyncio
async def test_registration_fail(simple_client: httpx.AsyncClient, user_service: UserService):
    data = {}
    response = await simple_client.post('/api/profile/registration', json=data)
    assert response.status_code == 422
    assert response.json() == {
        'detail': [
            {
                'type': 'missing',
                'loc': ['body', 'tg_name'],
                'msg': 'Field required',
                'input': {}
            },
            {
                'type': 'missing',
                'loc': ['body', 'email'],
                'msg': 'Field required',
                'input': {}
            },
            {
                'type': 'missing',
                'loc': ['body', 'password'],
                'msg': 'Field required',
                'input': {}
            }
        ]
    }
    assert len(await user_service.get_users()) == 2


@pytest_mark_asyncio
async def test_login(client: httpx.AsyncClient, user_service: UserService):
    data = {
        'tg_name': 'new_tg',
        'email': 'user@mail.ru',
        'password': 'test-password'
    }
    user = await user_service.create_user(**data)
    response = await client.post('/api/profile/login', json={'email': data['email'], 'password': data['password']})
    assert response.status_code == 200
