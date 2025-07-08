from fastapi import status
from fastapi.requests import Request
from fastapi.exceptions import HTTPException

from infra.db.repository.exceptions import RepositoryError
from service.exceptions import UserPermissionServiceError, UserAuthServiceError, ServiceError


def service_error_handler(request: Request, e: ServiceError):
    raise HTTPException(status.HTTP_400_BAD_REQUEST, e.detail)


def repository_error_handler(request: Request, e: RepositoryError):
    raise HTTPException(status.HTTP_400_BAD_REQUEST, e.detail)


def permission_error_handler(request: Request, e: UserPermissionServiceError):
    raise HTTPException(status.HTTP_403_FORBIDDEN, e.detail)


def auth_error(request: Request, e: UserAuthServiceError):
    code = status.HTTP_400_BAD_REQUEST
    internall_exc_class = e.detail.get('internal exception class', None)
    if internall_exc_class == 'TokenError':
        code = status.HTTP_401_UNAUTHORIZED
    raise HTTPException(code, e.detail)
