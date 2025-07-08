import pytest

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
def mock_group_repo(mocker):
    repo = mocker.Mock()
    repo.add_users_in_group = mocker.AsyncMock()
    repo.exclude_users_from_group = mocker.AsyncMock()
    return repo


@pytest.fixture
def mock_user_repo(mocker):
    repo = mocker.Mock()
    repo.get_user = mocker.AsyncMock()
    repo.get_users_by = mocker.AsyncMock()
    repo.get_user_by_email = mocker.AsyncMock()
    repo.get_user_and_tasks = mocker.AsyncMock()
    repo.get_user_and_groups = mocker.AsyncMock()
    repo.create_user = mocker.AsyncMock()
    repo.update_user = mocker.AsyncMock()
    return repo


@pytest.fixture
def mock_jwt_handler(mocker):
    return mocker.Mock()


@pytest.fixture
def mock_serializer_handler(mocker):
    return mocker.Mock()


@pytest.fixture
def task_service(mock_task_repo: TaskRepository, mock_user_repo: UserRepository):
    return TaskService(mock_task_repo, mock_user_repo)


@pytest.fixture
def user_service(mock_user_repo: UserRepository, mock_task_repo):
    return UserService(mock_user_repo, mock_task_repo)


@pytest.fixture
def auth_service(mock_user_repo: UserRepository):
    return UserAuthService(mock_user_repo)


@pytest.fixture
def permission_service():
    return UserPermissionService([])


@pytest.fixture
def group_service(mock_group_repo: GroupRepository, mock_user_repo: UserRepository):
    return GroupService(mock_group_repo, mock_user_repo)
