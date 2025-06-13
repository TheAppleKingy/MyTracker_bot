import pytest
import pytest_asyncio

from httpx import AsyncClient, ASGITransport
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db_session
from app import app
from security.authentication import access, refresh
from models.users import User, Group
from service.user_service import UserService


@pytest_asyncio.fixture
async def client(session: AsyncSession):
    app.dependency_overrides[get_db_session] = lambda: session
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client:
        yield client
    app.dependency_overrides.clear()


@pytest.fixture
def admin_client(client: AsyncClient, admin_user: User):
    access_token = access({'user_id': admin_user.id})
    refresh_token = refresh({'user_id': admin_user.id})
    client.cookies.set('access', access_token, domain='test.local')
    client.cookies.set('refresh', refresh_token, domain='test.local')
    return client


@pytest.fixture
def simple_client(client: AsyncClient, simple_user: User):
    access_token = access({'user_id': simple_user.id})
    refresh_token = refresh({'user_id': simple_user.id})
    client.cookies.set('access', access_token, domain='test.local')
    client.cookies.set('refresh', refresh_token, domain='test.local')
    return client
