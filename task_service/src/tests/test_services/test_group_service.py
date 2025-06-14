import pytest

from models.users import Group, User
from service.group_service import GroupService

pytest_mark_asyncio = pytest.mark.asyncio


@pytest_mark_asyncio
async def test_add_users_into_group(group_service: GroupService, simple_user: User):
    group = await group_service.create_obj(title='Other')
    assert group.users == []
    added = await group_service.add_users(group, [simple_user])
    assert added == [simple_user]
    assert group.users == [simple_user]
    add_again = await group_service.add_users(group, [simple_user])
    assert add_again == []
    assert group.users == [simple_user]


@pytest_mark_asyncio
async def test_exclude_users_from_group(group_service: GroupService, simple_user: User):
    group = await group_service.create_obj(title='Other')
    await group_service.add_users(group, [simple_user])
    assert group.users == [simple_user]
    deleted = await group_service.exclude_users(group, [simple_user])
    assert deleted == [simple_user]
    assert group.users == []
    deleted_again = await group_service.exclude_users(group, [simple_user])
    assert deleted_again == []
    assert group.users == []
