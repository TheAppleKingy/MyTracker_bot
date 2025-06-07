import pytest
import httpx

from models.models import User
from service.service import DBSocket
from schemas import UserViewSchema


pytest_mark_asyncio = pytest.mark.asyncio


@pytest_mark_asyncio
async def test_create_user(admin_client: httpx.AsyncClient, user_socket: DBSocket):
    data = {
        'tg_name': 'test_tg',
        'email': 'test_email@mail.com',
        'password': 'test_password'
    }
    result = await admin_client.post('/api/users', json=data)
    created_user = await user_socket.get_db_obj(User.tg_name == data['tg_name'])
    assert created_user is not None
    assert result.status_code == 201


@pytest_mark_asyncio
async def test_create_fail(admin_client: httpx.AsyncClient, user_socket: DBSocket):
    data = {
        'tg_name': 'test_tg',
        'password': 'test_password'
    }
    response = await admin_client.post('/api/users', json=data)
    assert response.status_code == 422
    assert response.json() == {'detail': [{'type': 'missing', 'loc': [
        'body', 'email'], 'msg': 'Field required', 'input': {'tg_name': 'test_tg', 'password': 'test_password'}}]}
    assert await user_socket.get_db_obj(User.tg_name == data['tg_name']) is None


@pytest_mark_asyncio
async def test_create_unauthorized(client: httpx.AsyncClient, user_socket: DBSocket):
    data = {
        'any': 'any'
    }
    response = await client.post('/api/users', json=data)
    assert response.status_code == 401
    assert response.json() == {'detail': {'error': 'token was not provide'}}


@pytest_mark_asyncio
async def test_get_user(admin_client: httpx.AsyncClient, user_socket: DBSocket, simple_user):
    response = await admin_client.get('/api/users/{}'.format(simple_user.id))
    assert response.status_code == 200
    assert response.json() == {
        'id': 9, 'tg_name': 'simple_user', 'email': 'simple@mail.ru'}


@pytest_mark_asyncio
async def test_get_users(admin_client: httpx.AsyncClient, user_socket: DBSocket, admin_user: User, simple_user: User):
    response = await admin_client.get('/api/users')
    simple_view_schema = UserViewSchema.model_validate(
        simple_user, from_attributes=True).model_dump()
    admin_view_schema = UserViewSchema.model_validate(
        admin_user, from_attributes=True).model_dump()
    assert response.status_code == 200
    assert response.json() == [admin_view_schema, simple_view_schema]
