import pytest
import pytest_asyncio

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from infra.db.models.tasks import Task
from infra.db.models.users import User, Group
from infra.db.repository.user_repo import UserRepository
from infra.db.repository.group_repo import GroupRepository
from infra.db.repository.task_repo import TaskRepository
from service.task_service import TaskService
from service.user_service import UserService, UserAuthService, UserPermissionService
from service.group_service import GroupService


@pytest.fixture
def mock_task_repo(mocker):
    return mocker.Mock()


@pytest.fixture
def mock_user_repo(mocker):
    repo = mocker.Mock()
    repo.get_user = mocker.AsyncMock()
    repo.get_user_by_email = mocker.AsyncMock()
    repo.get_user_and_tasks = mocker.AsyncMock()
    repo.get_user_and_groups = mocker.AsyncMock()
    repo.create_user = mocker.AsyncMock()
    return repo


@pytest.fixture
def task_service(mock_task_repo: TaskRepository, mock_user_repo: UserRepository):
    return TaskService(mock_task_repo, mock_user_repo)


@pytest.fixture
def user_service(mock_user_repo, mock_task_repo):
    return UserService(mock_user_repo, mock_task_repo)


@pytest.fixture
def auth_service(mock_user_repo):
    return UserAuthService(mock_user_repo)


@pytest.fixture
def permission_service(mock_user_repo):
    return UserPermissionService(mock_user_repo, allowed_group_name="admin")
