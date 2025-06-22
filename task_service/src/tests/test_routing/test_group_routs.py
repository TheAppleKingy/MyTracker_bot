import pytest
import httpx
import asyncio

from models.users import User, Group
from service.group_service import GroupService
from schemas.users_schemas import UserViewSchema
from schemas.groups_schemas import GroupVeiwSchema


pytest_mark_asyncio = pytest.mark.asyncio


@pytest_mark_asyncio
async def test_get_groups(admin_client: httpx.AsyncClient, group_service: GroupService):
    response = await admin_client.get('/api/groups')
    assert response.status_code == 200
    groups = await group_service.get_objs(Group.title.in_(['Admin', 'Other']))
    expected = [GroupVeiwSchema.model_validate(
        obj, from_attributes=True).model_dump() for obj in groups]
    assert response.json() == expected


@pytest_mark_asyncio
async def test_add_users_into_group(admin_client: httpx.AsyncClient, simple_user: User, admin_user: User, group_service: GroupService):
    data = {
        'users': [
            simple_user.id, simple_user.id
        ]
    }
    admin_gr = await group_service.get_obj(Group.title == 'Admin')
    assert admin_gr.users == [admin_user]
    response = await admin_client.patch('/api/groups/{}/add_users'.format(admin_gr.id), json=data)
    assert response.status_code == 200
    expected = UserViewSchema.model_validate(
        simple_user, from_attributes=True).model_dump()
    assert response.json() == [expected]
    assert admin_gr.users == [admin_user, simple_user]


@pytest_mark_asyncio
async def test_add_users_into_group_fail(admin_client: httpx.AsyncClient, simple_user: User, admin_user: User, group_service: GroupService):
    data = {
        'users': [
            admin_user.id+simple_user.id
        ]
    }
    admin_gr = await group_service.get_obj(Group.title == 'Admin')
    assert admin_gr.users == [admin_user]
    response = await admin_client.patch('/api/groups/{}/add_users'.format(admin_gr.id), json=data)
    assert response.status_code == 400
    assert response.json() == {'detail': '"User" objects with next "id"s do not exist: {}'.format(
        data['users'][0])}
    assert admin_gr.users == [admin_user]


@pytest_mark_asyncio
async def test_exclude_users_from_group(admin_client: httpx.AsyncClient, simple_user: User, admin_user: User, group_service: GroupService):
    data = {
        'users': [
            simple_user.id
        ]
    }
    admin_gr = await group_service.get_obj(Group.title == 'Admin')
    await group_service.add_users(admin_gr, [simple_user])
    assert admin_gr.users == [admin_user, simple_user]
    response = await admin_client.patch('/api/groups/{}/exclude_users'.format(admin_gr.id), json=data)
    expected = UserViewSchema.model_validate(
        simple_user, from_attributes=True).model_dump()
    assert response.status_code == 200
    assert response.json() == [expected]
    assert admin_gr.users == [admin_user]


@pytest_mark_asyncio
async def test_exclude_users_from_group_fail(admin_client: httpx.AsyncClient, simple_user: User, admin_user: User, group_service: GroupService):
    data = {
        'users': [
            simple_user.id+admin_user.id
        ]
    }
    admin_gr = await group_service.get_obj(Group.title == 'Admin')
    assert admin_gr.users == [admin_user]
    response = await admin_client.patch('/api/groups/{}/exclude_users'.format(admin_gr.id), json=data)
    assert response.status_code == 400
    assert response.json() == {
        'detail': '"User" objects with next "id"s do not exist: {}'.format(data['users'][0])}
    assert admin_gr.users == [admin_user]


@pytest_mark_asyncio
async def test_forbidden(simple_client: httpx.AsyncClient):
    get = simple_client.get('/api/groups')
    add_users = simple_client.patch('/api/groups/1/add_users')
    exclude_users = simple_client.patch('/api/groups/1/exclude_users')
    get_resp, add_users_resp, exclude_users_resp = await asyncio.gather(get, add_users, exclude_users)
    assert get_resp.status_code == 403
    assert add_users_resp.status_code == 403
    assert exclude_users_resp.status_code == 403
