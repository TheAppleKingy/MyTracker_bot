from fastapi import FastAPI


app = FastAPI()


def include_routers():
    from routing.user_routs import user_router
    from routing.auth_routs import profile_router
    from routing.groups_routs import group_router
    from routing.task_routs import task_router
    from routing.api_for_bot import bot_router
    app.include_router(user_router)
    app.include_router(profile_router)
    app.include_router(group_router)
    app.include_router(task_router)
    app.include_router(bot_router)


include_routers()
