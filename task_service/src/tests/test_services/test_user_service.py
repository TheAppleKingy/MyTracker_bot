import pytest

from infra.db.models.tasks import Task
from infra.db.models.users import User, Group
from infra.db.repository.user_repo import UserRepository
from infra.db.repository.exceptions import UserRepositoryError
from infra.exc import ServiceError
from infra.security.jwt import get_token_for_user
from service.user_service import UserAuthService, UserPermissionService, UserService
from service.exceptions import UserAuthServiceError, UserPermissionServiceError
from api.schemas.users_schemas import LoginSchema, UserCreateSchema


pytest_mark_asyncio = pytest.mark.asyncio


@pytest_mark_asyncio
async def test_get_user_tasks_success(user_service: UserService, mock_user_repo: UserRepository):
    tasks = [Task(id=1), Task(id=2)]
    mock_user_repo.get_user_and_tasks.return_value = User(id=1, tasks=tasks)
    result = await user_service.get_user_tasks(1)
    assert result == tasks
    mock_user_repo.get_user_and_tasks.assert_awaited_once_with(1)


"""Testing auth service"""


@pytest_mark_asyncio
async def test_auth_user_success(auth_service: UserAuthService, mock_user_repo: UserRepository, mocker):
    user = User(id=1)
    token = get_token_for_user(user)
    mock_user_repo.get_user.return_value = user
    result = await auth_service.auth_user(token)
    assert result == user


@pytest_mark_asyncio
async def test_auth_user_fail_invalid_id(auth_service: UserAuthService, mock_user_repo: UserRepository, mocker):
    mock_user_repo.get_user.return_value = None
    token = get_token_for_user(User(id=1))
    with pytest.raises(UserAuthServiceError, match="Security threat"):
        await auth_service.auth_user(token)


@pytest_mark_asyncio
async def test_login_user_success(auth_service: UserAuthService, mock_user_repo: UserRepository, mocker):
    user = User(email="test@example.com", password="hashed")
    mock_user_repo.get_user_by_email.return_value = user
    schema = LoginSchema(email=user.email, password=user.password)
    mocker.patch("service.user_service.check_password", return_value=True)
    result = await auth_service.login_user(schema)
    assert result == user


@pytest_mark_asyncio
async def test_login_user_wrong_password(auth_service: UserAuthService, mock_user_repo: UserRepository, mocker):
    user = User(email="test@example.com", password="hashed")
    mock_user_repo.get_user_by_email.return_value = user
    mocker.patch("service.user_service.check_password", return_value=False)
    schema = LoginSchema(email=user.email, password=user.password)
    with pytest.raises(UserAuthServiceError, match="Wrong password"):
        await auth_service.login_user(schema)


@pytest_mark_asyncio
async def test_login_user_not_found(auth_service: UserAuthService, mock_user_repo: UserRepository, mocker):
    mock_user_repo.get_user_by_email.return_value = None
    schema = LoginSchema(email='te', password='tp')
    with pytest.raises(ServiceError, match="Unable to find user"):
        await auth_service.login_user(schema)


@pytest_mark_asyncio
async def test_register_user_success(auth_service: UserAuthService, mock_user_repo: UserRepository, mocker):
    user = User(id=1, email="test@test.com")
    mock_user_repo.create_user.return_value = user
    schema = UserCreateSchema(
        tg_name='testtg', email='test@test.com', password='test_pass')
    result = await auth_service.register_user(schema)
    assert result == user
    mock_user_repo.create_user.assert_awaited_once()


@pytest_mark_asyncio
async def test_register_user_fail_duplicate(auth_service: UserAuthService, mock_user_repo: UserRepository, mocker):
    mock_user_repo.create_user.side_effect = UserRepositoryError(
        'already exists')
    mocker.patch("service.user_service.parse_integrity_err_msg",
                 return_value="email")
    schema = UserCreateSchema(
        tg_name='testtg', email='lala@mail.ru', password='test_pass')
    with pytest.raises(UserRepositoryError, match="already exists"):
        await auth_service.register_user(schema)


@pytest_mark_asyncio
async def test_check_permission_success(permission_service: UserPermissionService, mock_user_repo: UserRepository):
    group = Group(title="admin")
    user = User(id=1, groups=[group])
    mock_user_repo.get_user_and_groups.return_value = user
    result = await permission_service.check(1)
    assert result == user


@pytest_mark_asyncio
async def test_check_permission_fail(permission_service: UserPermissionService, mock_user_repo: UserRepository):
    group = Group(title="user")
    user = User(id=1, groups=[group])
    mock_user_repo.get_user_and_groups.return_value = user
    with pytest.raises(UserPermissionServiceError, match="no permissions"):
        await permission_service.check(1)
