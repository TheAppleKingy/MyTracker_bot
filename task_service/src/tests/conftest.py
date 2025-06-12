import pytest
import pytest_asyncio
import os
import asyncpg

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncEngine

from config import FORMATTED_DATABASE_URL, TEST_DATABASE_URL
from models.base import Base
from models.users import User, Group
from service.factories import UserServiceFactory, GroupServiceFactory
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


@pytest.fixture
def user_service(session):
    socket = SocketFactory.get_socket(User, session)
    user_service = UserServiceFactory.get_service(socket)
    return user_service


@pytest.fixture
def group_service(session):
    socket = SocketFactory.get_socket(Group, session)
    group_service = GroupServiceFactory.get_service(socket)
    return group_service
