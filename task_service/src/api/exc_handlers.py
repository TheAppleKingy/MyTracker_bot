from fastapi import status
from fastapi.requests import Request
from fastapi.exceptions import HTTPException

from infra.exc import ServiceError, RepositoryError
from service.exceptions import UserPermissionServiceError, UserAuthServiceError


def service_error_handler(request: Request, e: ServiceError):
    raise HTTPException(status.HTTP_400_BAD_REQUEST, e.detail)


def repository_error_handler(request: Request, e: RepositoryError):
    raise HTTPException(status.HTTP_400_BAD_REQUEST, e.detail)


def permission_error_handler(request: Request, e: UserPermissionServiceError):
    raise HTTPException(status.HTTP_403_FORBIDDEN, e.detail)
