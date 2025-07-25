import pytest
import httpx
import asyncio

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities.users import User
from infra.db.tables.associations import users_groups
from application.dto.users_dto import UserView, UserUpdate


pytest_mark_asyncio = pytest.mark.asyncio


@pytest_mark_asyncio
async def test_create_user(admin_client: httpx.AsyncClient, session: AsyncSession):
    data = {
        'tg_name': 'test_tg',
        'email': 'test_email@mail.com',
        'password': 'test_password'
    }
    result = await admin_client.post('/api/users', json=data)
    res = await session.execute(select(User).where(User.email == data['email']))
    created_user = res.scalar_one_or_none()
    assert created_user is not None
    assert result.status_code == 201


@pytest_mark_asyncio
async def test_create_already_exists(admin_client: httpx.AsyncClient):
    data = {
        'tg_name': 'admin',
        'email': 'kaska',
        'password': 'test_password'
    }
    response = await admin_client.post('/api/users', json=data)
    assert response.status_code == 400
    assert response.json() == {'detail': {'repository': 'UserRepository',
                                          'internal exception class': 'IntegrityError', 'msgs': ['Key (tg_name)=(admin) already exists.']}}


@pytest_mark_asyncio
async def test_get_user(admin_client: httpx.AsyncClient, simple_user: User):
    response = await admin_client.get('/api/users/{}'.format(simple_user.id))
    assert response.status_code == 200
    assert response.json() == UserView.model_validate(
        simple_user, from_attributes=True).model_dump()


@pytest_mark_asyncio
async def test_get_user_none(admin_client: httpx.AsyncClient):
    response = await admin_client.get('/api/users/0')
    assert response.status_code == 200
    assert response.json() == None


@pytest_mark_asyncio
async def test_get_users(admin_client: httpx.AsyncClient, admin_user: User, simple_user: User):
    response = await admin_client.get('/api/users')
    expected = [UserView.model_validate(
        obj, from_attributes=True).model_dump() for obj in [admin_user, simple_user]]
    assert response.status_code == 200
    assert response.json() == expected


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
    assert response.json() == [UserView.model_validate(
        simple_user, from_attributes=True).model_dump()]
    assert simple_user.email == data['email']
    assert simple_user.first_name == data['first_name']


@pytest_mark_asyncio
async def test_delete(admin_client: httpx.AsyncClient, simple_user: User, session: AsyncSession):
    id = simple_user.id
    query = select(users_groups).where(users_groups.c.user_id == id)
    res = await session.execute(query)
    assert res.scalars().all() != []
    response = await admin_client.delete('/api/users/{}'.format(id))
    assert response.status_code == 204
    res = await session.execute(select(User).where(User.id == id))
    user = res.scalar_one_or_none()
    assert user is None


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
