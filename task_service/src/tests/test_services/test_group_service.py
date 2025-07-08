import pytest

from infra.db.models.users import User
from infra.db.repository.group_repo import GroupRepository
from infra.db.repository.user_repo import UserRepository
from service.group_service import GroupService
from service.exceptions import GroupServiceException


pytest_mark_asyncio = pytest.mark.asyncio


@pytest_mark_asyncio
async def test_add_users(mock_group_repo: GroupRepository, mock_user_repo: UserRepository, group_service: GroupService):
    users = [User(id=1), User(id=2)]
    mock_user_repo.get_users_by.return_value = users
    mock_group_repo.add_users_in_group.return_value = users
    added = await group_service.add_users(1, [1, 2])
    assert added == users


@pytest_mark_asyncio
async def test_add_users_into_group_fail(mock_user_repo: UserRepository, group_service: GroupService):
    users = [User(id=1), User(id=2)]
    mock_user_repo.get_users_by.return_value = users
    with pytest.raises(GroupServiceException, match='"User" objects with next "id"s do not exist: '):
        await group_service.add_users(1, [1, 2, 3])


@pytest_mark_asyncio
async def test_exclude_users(mock_group_repo: GroupRepository, mock_user_repo: UserRepository, group_service: GroupService):
    users = [User(id=1), User(id=2)]
    mock_user_repo.get_users_by.return_value = users
    mock_group_repo.exclude_users_from_group.return_value = users
    added = await group_service.exclude_users(1, [1, 2])
    assert added == users


@pytest_mark_asyncio
async def test_exclude_users_fail(mock_user_repo: UserRepository, group_service: GroupService):
    users = [User(id=1), User(id=2)]
    mock_user_repo.get_users_by.return_value = users
    with pytest.raises(GroupServiceException, match='"User" objects with next "id"s do not exist: '):
        await group_service.add_users(1, [1, 2, 3])
