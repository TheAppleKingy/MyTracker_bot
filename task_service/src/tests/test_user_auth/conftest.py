import pytest
import pytest_asyncio
import asyncio
import os
import asyncpg

from httpx import AsyncClient, ASGITransport
from unittest.mock import MagicMock
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncEngine, AsyncSession

from dependencies import get_user_allowed_by_group, jwt_authentication
from database import get_db_session
from config import FORMATTED_DATABASE_URL, TEST_DATABASE_URL
from app import app
from security.authentication import access, refresh
from models.base import Base
from models.users import User, Group
from service.factories import UserServiceFactory, GroupServiceFactory
from service.user_service import UserService
from repository.socket import SocketFactory


test_db_name = os.getenv('TEST_DB_NAME')
init_test_query = f"CREATE DATABASE {test_db_name}"
close_test_query = f"DROP DATABASE IF EXISTS {test_db_name}"


@pytest_asyncio.fixture(scope="session", autouse=True)
async def prepare_database():
    admin_conn = await asyncpg.connect(FORMATTED_DATABASE_URL)
    await admin_conn.execute(f"DROP DATABASE IF EXISTS {test_db_name} WITH (FORCE)")
    await admin_conn.execute(f"CREATE DATABASE {test_db_name}")
    await admin_conn.close()
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()
    admin_conn = await asyncpg.connect(FORMATTED_DATABASE_URL)
    await admin_conn.execute(f"DROP DATABASE IF EXISTS {test_db_name} WITH (FORCE)")
    await admin_conn.close()


@pytest_asyncio.fixture
async def engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def session(engine: AsyncEngine):
    session_maker = async_sessionmaker(bind=engine, expire_on_commit=False)
    async with session_maker() as session:
        for table in reversed(Base.metadata.sorted_tables):
            await session.execute(table.delete())
        await session.commit()
        yield session
        await session.rollback()


@pytest_asyncio.fixture(autouse=True)
async def setup(session: AsyncSession):
    admin_group = Group(title='Admin')
    group = Group(title='Other')
    session.add_all([admin_group, group])
    admin = User(tg_name='admin', email='admin@mail.ru',
                 password='test_password', groups=[admin_group])
    simple_user = User(tg_name='simple_user', email='simple@mail.ru',
                       password='test_password', groups=[group])
    session.add_all([admin, simple_user])
    await session.commit()


@pytest.fixture
def user_service(session):
    socket = SocketFactory.get_socket(User, session)
    user_service = UserServiceFactory.get_service(socket)
    return user_service


@pytest_asyncio.fixture
async def admin_user(user_service: UserService):
    return await user_service.get_user(User.tg_name == 'admin')


@pytest_asyncio.fixture
async def simple_user(user_service: UserService):
    return await user_service.get_user(User.tg_name == 'simple_user')


@pytest_asyncio.fixture
async def admin_access_token(admin_user: User):
    access_token = access({'user_id': admin_user.id})
    return access_token


@pytest_asyncio.fixture
async def simple_access_token(simple_user: User):
    access_token = access({'user_id': simple_user.id})
    return access_token


@pytest_asyncio.fixture
async def client(session: AsyncSession):
    app.dependency_overrides[get_db_session] = lambda: session
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client:
        yield client
    app.dependency_overrides.clear()


@pytest.fixture
def admin_client(client: AsyncClient, admin_access_token: str):
    client.cookies.set('access', admin_access_token)
    return client


@pytest.fixture
def simple_client(client: AsyncClient, simple_access_token: str):
    client.cookies.set('access', simple_access_token)
    return client
