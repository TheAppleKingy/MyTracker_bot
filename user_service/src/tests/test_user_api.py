import pytest
import httpx
import asyncio

from models.models import User
from models.associations import users_groups
from service.user_service import UserService
from schemas import UserViewSchema, UserUpdateSchema

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


pytest_mark_asyncio = pytest.mark.asyncio


@pytest_mark_asyncio
async def test_create_user(admin_client: httpx.AsyncClient, user_service: UserService):
    data = {
        'tg_name': 'test_tg',
        'email': 'test_email@mail.com',
        'password': 'test_password'
    }
    result = await admin_client.post('/api/users', json=data)
    created_user = await user_service.get_user(User.tg_name == data['tg_name'])
    assert created_user is not None
    assert result.status_code == 201


@pytest_mark_asyncio
async def test_create_fail(admin_client: httpx.AsyncClient, user_service: UserService):
    data = {
        'tg_name': 'test_tg',
        'password': 'test_password'
    }
    response = await admin_client.post('/api/users', json=data)
    assert response.status_code == 422
    assert response.json() == {'detail': [{'type': 'missing', 'loc': [
        'body', 'email'], 'msg': 'Field required', 'input': {'tg_name': 'test_tg', 'password': 'test_password'}}]}
    assert await user_service.get_user(User.tg_name == data['tg_name']) is None


@pytest_mark_asyncio
async def test_create_unauthorized(client: httpx.AsyncClient):
    data = {
        'any': 'any'
    }
    response = await client.post('/api/users', json=data)
    assert response.status_code == 401
    assert response.json() == {'detail': {'error': 'token was not provide'}}


@pytest_mark_asyncio
async def test_get_user(admin_client: httpx.AsyncClient, simple_user):
    response = await admin_client.get('/api/users/{}'.format(simple_user.id))
    assert response.status_code == 200
    assert response.json() == {
        'id': 9, 'tg_name': 'simple_user', 'email': 'simple@mail.ru'}


@pytest_mark_asyncio
async def test_get_users(admin_client: httpx.AsyncClient, admin_user: User, simple_user: User):
    response = await admin_client.get('/api/users')
    simple_view_schema = UserViewSchema.model_validate(
        simple_user, from_attributes=True).model_dump()
    admin_view_schema = UserViewSchema.model_validate(
        admin_user, from_attributes=True).model_dump()
    assert response.status_code == 200
    assert response.json() == [admin_view_schema, simple_view_schema]


@pytest_mark_asyncio
async def test_get_unauthorized(client: httpx.AsyncClient):
    response = await client.get('/api/users')
    assert response.status_code == 401


@pytest_mark_asyncio
async def test_update(admin_client: httpx.AsyncClient, simple_user: User):
    data = {
        'email': 'updated@mail.com',
        'first_name': 'simple'
    }
    assert simple_user.email != data['email']
    assert simple_user.first_name != data['first_name']
    response = await admin_client.patch('/api/users/{}'.format(simple_user.id), json=data)
    assert response.status_code == 200
    assert response.json() == [UserUpdateSchema.model_validate(
        simple_user, from_attributes=True).model_dump()]
    assert simple_user.email == data['email']
    assert simple_user.first_name == data['first_name']


@pytest_mark_asyncio
async def test_update_unauthorized(client: httpx.AsyncClient, simple_user: User):
    data = {
        'email': 'updated@mail.com',
        'first_name': 'simple'
    }
    response = await client.patch('/api/users/{}'.format(simple_user.id), json=data)
    assert response.status_code == 401


@pytest_mark_asyncio
async def test_delete(admin_client: httpx.AsyncClient, user_service: UserService, simple_user: User, session: AsyncSession):
    id = simple_user.id
    query = select(users_groups).where(users_groups.c.user_id == id)
    res = await session.execute(query)
    assert res.scalars().all() != []
    response = await admin_client.delete('/api/users/{}'.format(id))
    assert response.status_code == 204
    assert await user_service.get_user(User.id == id) is None
    res2 = await session.execute(query)
    assert res2.scalars().all() == []


@pytest_mark_asyncio
async def test_delete_unathorized(client: httpx.AsyncClient, simple_user: User):
    response = await client.delete('/api/users/{}'.format(simple_user.id))
    assert response.status_code == 401


@pytest_mark_asyncio
async def test_forbidden(simple_client: httpx.AsyncClient, simple_user: User):
    part_url = '/api/users/{}'.format(simple_user.id)
    url = '/api/users'
    get_task = simple_client.get(url)
    gets_task = simple_client.get(part_url)
    delete_task = simple_client.delete(part_url)
    update_task = simple_client.patch(part_url)
    post_task = simple_client.post(url)
    get, gets, delete, update, post = await asyncio.gather(get_task, gets_task, delete_task, update_task, post_task)
    assert get.status_code == 403
    assert gets.status_code == 403
    assert delete.status_code == 403
    assert update.status_code == 403
    assert post.status_code == 403
