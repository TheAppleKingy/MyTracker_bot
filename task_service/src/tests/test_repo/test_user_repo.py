import pytest

from infra.db.repository.user_repo import UserRepository
from infra.db.repository.exceptions import UserRepositoryError
from infra.db.models.users import User


pytest_mark_asyncio = pytest.mark.asyncio


@pytest_mark_asyncio
async def get_user(simple_user: User, user_repo: UserRepository):
    user = await user_repo.get_user(simple_user.id)
    assert user == simple_user


@pytest_mark_asyncio
async def get_user_none(user_repo: UserRepository):
    user = await user_repo.get_user(0)
    assert user is None


@pytest_mark_asyncio
async def test_user_by_email(simple_user: User, user_repo: UserRepository):
    user = await user_repo.get_user_by_email(simple_user.email)
    assert user == simple_user


@pytest_mark_asyncio
async def test_user_by_email_none(user_repo: UserRepository):
    user = await user_repo.get_user_by_email('s')
    assert user is None


@pytest_mark_asyncio
async def get_user_tasks(simple_user: User, user_repo: UserRepository):
    user = await user_repo.get_user_and_tasks(simple_user.id)
    assert user == simple_user
    assert user.tasks == []


@pytest_mark_asyncio
async def test_create(user_repo: UserRepository):
    data = {
        'tg_name': 'test',
        'email': 'test',
        'password': 'test_password'
    }
    created = await user_repo.create_user(**data)
    assert created.tg_name == data['tg_name']
    assert created.email == data['email']


@pytest_mark_asyncio
async def test_create_already_exists(simple_user: User, user_repo: UserRepository):
    data = {
        'tg_name': simple_user.tg_name,
        'email': 'test',
        'password': 'test_password'
    }
    with pytest.raises(UserRepositoryError):
        await user_repo.create_user(**data)


@pytest_mark_asyncio
async def test_delete(simple_user: User, user_repo: UserRepository):
    deleted = await user_repo.delete_user(simple_user.id)
    assert deleted[0].tg_name == simple_user.tg_name
    assert await user_repo.get_user(simple_user.id) is None


@pytest_mark_asyncio
async def test_update(simple_user: User, user_repo: UserRepository):
    assert simple_user.first_name is None
    data = {
        'first_name': 'lala'
    }
    await user_repo.update_user(simple_user.id, **data)
    assert simple_user.first_name == data['first_name']
