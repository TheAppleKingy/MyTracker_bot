from sqlalchemy.exc import IntegrityError

from infra.db.models.users import User
from infra.db.models.tasks import Task
from infra.db.repository.user_repo import UserRepository
from infra.db.repository.task_repo import TaskRepository
from infra.security.password_utils import hash_password, check_password
from infra.security.jwt import validate_token
from infra.exc import parse_integrity_err_msg, RepositoryError
from api.schemas.task_schemas import TaskCreateForUserSchema, TaskUpdateSchema
from api.schemas.users_schemas import LoginSchema, UserCreateSchema
from .exceptions import UserServiceError, UserAuthServiceError, UserPermissionServiceError


class BaseUserService:
    def __init__(self, user_repository: UserRepository):
        self.repo = user_repository


class UserService(BaseUserService):
    def __init__(self, user_repository, task_repository: TaskRepository):
        super().__init__(user_repository)
        self.task_repo = task_repository

    async def get_user_tasks(self, user_id: int) -> list[Task]:
        user = await self.repo.get_user_and_tasks(user_id)
        return user.tasks


class UserAuthService(BaseUserService):
    async def auth_user(self, token: str):
        payload = validate_token(token, ['user_id'])
        user_id = payload['user_id']
        user = await self.repo.get_user(user_id)
        if not user:
            raise UserAuthServiceError(
                'Not existing user_id was set in token payload. Security threat!')
        return user

    async def login_user(self, login_schema: LoginSchema):
        email, password = login_schema.email, login_schema.password
        user = await self.repo.get_user_by_email(email)
        if not user:
            raise UserAuthServiceError(
                f'Unable to find user with email ({email})')
        if not check_password(password, user.password):
            raise UserAuthServiceError(
                'Wrong password')
        return user

    async def register_user(self, register_schema: UserCreateSchema) -> User:
        raw_password = register_schema.password
        password = hash_password(raw_password)
        register_schema.password = password
        return await self.repo.create_user(**register_schema.model_dump(exclude_none=True))


class UserPermissionService(BaseUserService):
    def __init__(self, user_repository: UserRepository, allowed_group_name: str):
        super().__init__(user_repository)
        self.allowed_group_name = allowed_group_name

    async def check(self, user_id: int) -> User:
        user = await self.repo.get_user_and_groups(user_id)
        if not any([group.title == self.allowed_group_name for group in user.groups]):
            raise UserPermissionServiceError('User has no permissions')
        return user
