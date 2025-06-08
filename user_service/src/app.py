from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)


def include_routers():
    from routing.user_api import user_router
    from routing.auth import profile_router
    from routing.groups import group_router
    app.include_router(user_router)
    app.include_router(profile_router)
    app.include_router(group_router)


include_routers()
