from fastapi import FastAPI

app = FastAPI()


def include_routers():
    from routing.user_api import user_router
    app.include_router(user_router)


include_routers()
