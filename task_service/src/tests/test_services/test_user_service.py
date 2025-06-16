import pytest

from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine, async_sessionmaker

from models.users import User
from service.user_service import UserService
from service.exceptions import ServiceError
from security.password_utils import is_hashed


pytest_mark_asyncio = pytest.mark.asyncio


@pytest_mark_asyncio
async def test_get_methods(user_service: UserService, simple_user: User, admin_user: User):
    simple = await user_service.get_obj(User.tg_name == simple_user.tg_name)
    assert simple is not None
    with pytest.raises(ServiceError):
        not_exist = await user_service.get_obj(User.tg_name == '[pas[o]]', raise_exception=True)
        assert not_exist is None

    users = await user_service.get_objs(User.tg_name.in_([simple_user.tg_name, admin_user.tg_name]))
    assert users != []
    assert len(users) == 2
    assert admin_user in users
    assert simple_user in users


@pytest_mark_asyncio
async def test_create_user(user_service: UserService, session: AsyncSession):
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


@pytest_mark_asyncio
async def test_create_users(user_service: UserService, session: AsyncSession):
    data = [
        {
            'tg_name': 'new_tg',
            'email': 'user@mail.ru',
            'password': 'test-password'
        },
        {
            'tg_name': 'new_tg2',
            'email': 'user2@mail.ru',
            'password': 'test-password'
        }
    ]
    created = await user_service.create_objs(table_raws=data)
    assert created != []
    assert len(created) == 2
    query = select(User).where(User.tg_name.in_(['new_tg', 'new_tg2']))
    res = await session.execute(query)
    users = res.scalars().all()
    assert users != []
    assert len(users) == 2
    assert created[0] in users
    assert created[1] in users


@pytest_mark_asyncio
async def test_password(user_service: UserService):
    data = {
        'tg_name': 'new_tg',
        'email': 'user@mail.ru',
        'password': 'test-password'
    }
    created = await user_service.create_obj(**data)
    assert is_hashed(created.password)
    assert user_service.check_password(created, data['password'])
    assert not user_service.check_password(created, 'asasf')
    await user_service.set_password(created, 'another_pas')
    assert user_service.check_password(created, 'another_pas')


@pytest_mark_asyncio
async def test_create_user_fail(user_service: UserService, session: AsyncSession):
    data = {
        'tg_name': 'new_tg',
        'email': 'user@mail.ru',
    }
    with pytest.raises(KeyError):
        created = await user_service.create_obj(**data)
        assert created is None
    query = select(User).where(User.tg_name == 'new_tg')
    res = await session.execute(query)
    not_created = res.scalar_one_or_none()
    assert not_created is None


@pytest_mark_asyncio
async def test_create_users_fail(user_service: UserService, session: AsyncSession):
    many_data = [
        {
            'tg_name': 'new_tg',
            'password': 'test_pas'
        },
        {
            'email': 'papa',
            'password': 'test_pas'
        }
    ]
    with pytest.raises(ServiceError):
        created = await user_service.create_objs(many_data)
        assert created is None
    query = select(User).where(
        or_(User.tg_name == 'new_tg', User.email == 'papa'))
    res = await session.execute(query)
    assert res.scalars().all() == []


@pytest_mark_asyncio
async def test_get_column_methods(user_service: UserService, simple_user: User, admin_user: User):
    tgs = await user_service.get_column_vals(User.tg_name, User.email.in_([simple_user.email, admin_user.email]))
    assert tgs == [admin_user.tg_name, simple_user.tg_name]
    tgs_ids = await user_service.get_columns_vals([User.tg_name, User.id], User.email == admin_user.email)
    assert tgs_ids == [(admin_user.tg_name, admin_user.id)]


@pytest_mark_asyncio
async def test_delete(user_service: UserService, simple_user: User, admin_user: User, session: AsyncSession):
    deleted = await user_service.delete(User.tg_name == simple_user.tg_name, User.email == admin_user.email)
    assert deleted == []
    query = select(User).where(
        or_(User.tg_name == simple_user.tg_name, User.email == admin_user.email))
    res = await session.execute(query)
    users = res.scalars().all()
    assert users == [admin_user, simple_user]

    deleted = await user_service.delete(User.tg_name == simple_user.tg_name)
    assert len(deleted) == 1
    assert deleted[0].email == simple_user.email
    query = select(User).where(User.email == simple_user.email)
    res = await session.execute(query)
    users = res.scalars().all()
    assert users == []


@pytest_mark_asyncio
async def test_update(user_service: UserService, simple_user: User, session: AsyncSession):
    assert simple_user.first_name is None
    updated_simple = await user_service.update(User.id == simple_user.id, first_name='simple_first')
    assert updated_simple[0].first_name == 'simple_first'
    query = select(User).where(User.first_name == 'simple_first')
    res = await session.execute(query)
    updated_simple = res.scalar_one_or_none()
    assert updated_simple is not None


@pytest_mark_asyncio
async def test_create_no_commit(user_service: UserService, engine: AsyncEngine, session: AsyncSession):
    data = {
        'tg_name': 'new_tg',
        'email': 'user@mail.ru',
        'password': 'test-password'
    }
    created = await user_service.create_obj(commit=False, **data)
    assert created is not None
    async with async_sessionmaker(engine, expire_on_commit=False)() as session:
        query = select(User).where(User.tg_name == data['tg_name'])
        res = await session.execute(query)
        user = res.scalar_one_or_none()
        assert user is None


@pytest_mark_asyncio
async def test_update_no_commit(user_service: UserService, simple_user: User, engine: AsyncEngine, session: AsyncSession):
    assert simple_user.first_name is None
    updated_simple = await user_service.update(User.id == simple_user.id, first_name='simple_first', commit=False)
    assert updated_simple[0].first_name == 'simple_first'
    async with async_sessionmaker(engine, expire_on_commit=False)() as session:
        query = select(User).where(User.first_name == 'simple_first')
        res = await session.execute(query)
        updated_simple = res.scalar_one_or_none()
        assert updated_simple is None


@pytest_mark_asyncio
async def test_delete_no_commit(user_service: UserService, simple_user: User, engine: AsyncEngine, session: AsyncSession):
    deleted = await user_service.delete(User.tg_name == simple_user.tg_name, commit=False)
    assert len(deleted) == 1
    assert deleted[0].email == simple_user.email
    async with async_sessionmaker(engine, expire_on_commit=False)() as session:
        query = select(User).where(User.email == simple_user.email)
        res = await session.execute(query)
        users = res.scalars().all()
        assert len(users) == 1
        assert users[0].tg_name == simple_user.tg_name
