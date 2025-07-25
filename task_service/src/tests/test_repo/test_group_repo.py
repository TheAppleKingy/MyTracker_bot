import pytest

from domain.entities.users import User, Group
from infra.db.repository.group_repo import GroupRepository


pytest_mark_asyncio = pytest.mark.asyncio


@pytest_mark_asyncio
async def test_add_users(admin_group: Group, group_repo: GroupRepository, simple_user: User, admin_user: User):
    assert admin_group.users == [admin_user]
    added = await group_repo.add_users_in_group(admin_group.id, [simple_user])
    assert added == [simple_user]
    assert len(admin_group.users) == 2
    assert simple_user in admin_group.users


@pytest_mark_asyncio
async def test_already_in_gr(admin_group: Group, group_repo: GroupRepository, admin_user: User):
    assert admin_group.users == [admin_user]
    added = await group_repo.add_users_in_group(admin_group.id, [admin_user])
    assert added == []
    assert admin_group.users == [admin_user]


@pytest_mark_asyncio
async def test_exclude(admin_group: Group, group_repo: GroupRepository, admin_user: User):
    assert admin_group.users == [admin_user]
    excluded = await group_repo.exclude_users_from_group(admin_group.id, [admin_user])
    assert excluded == [admin_user]
    assert admin_group.users == []


@pytest_mark_asyncio
async def test_exclude_not_in_gr(admin_group: Group, group_repo: GroupRepository, simple_user: User, admin_user: User):
    assert admin_group.users == [admin_user]
    excluded = await group_repo.exclude_users_from_group(admin_group.id, [simple_user])
    assert excluded == []
    assert admin_group.users == [admin_user]
