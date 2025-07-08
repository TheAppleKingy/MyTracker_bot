from fastapi import FastAPI


app = FastAPI()


def include_routers():
    from api.routing.user_routs import user_router
    from api.routing.auth_routs import profile_router
    from api.routing.groups_routs import group_router
    from api.routing.task_routs import task_router
    from api.routing.api_for_bot import bot_router
    app.include_router(user_router)
    app.include_router(profile_router)
    app.include_router(group_router)
    app.include_router(task_router)
    app.include_router(bot_router)


def include_exc_handlers():
    from api.exc_handlers import (
        service_error_handler,
        permission_error_handler,
        repository_error_handler,
        auth_error
    )
    from infra.db.repository.exceptions import RepositoryError
    from service.exceptions import UserPermissionServiceError, ServiceError, UserAuthServiceError
    app.add_exception_handler(ServiceError, service_error_handler)
    app.add_exception_handler(
        UserPermissionServiceError, permission_error_handler)
    app.add_exception_handler(RepositoryError, repository_error_handler)
    app.add_exception_handler(UserAuthServiceError, auth_error)


include_routers()
include_exc_handlers()
