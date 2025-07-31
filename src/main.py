import asyncio

import watchfiles

import config

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage

from handlers.auth.login import login_router
from handlers.auth.registration import registration_router
from handlers.start import start_router
from handlers.tasks.show_tasks import show_task_router
from handlers.tasks.create_tasks import create_task_router
from handlers.tasks.update_task import update_task_router
from handlers.tasks.task_reminder import reminder_router
from handlers.settings.cmd_settings import settings_router
from handlers.settings.set_tz import tz_router
from handlers.tasks.delete_task import delete_task_router

from api.redis_client import redis

from middleware import BackendResponseMiddleware, RollbackDetectorMiddleware


bot = Bot(config.TOKEN)
redis_storage = RedisStorage(redis)
dispatcher = Dispatcher(storage=redis_storage)
dispatcher.message.middleware(BackendResponseMiddleware())
dispatcher.message.middleware(RollbackDetectorMiddleware())
dispatcher.callback_query.middleware(BackendResponseMiddleware())
dispatcher.callback_query.middleware(RollbackDetectorMiddleware())


async def start():
    dispatcher.include_routers(
        start_router,
        login_router,
        registration_router,
        show_task_router,
        create_task_router,
        update_task_router,
        reminder_router,
        settings_router,
        tz_router,
        delete_task_router
    )
    await dispatcher.start_polling(bot)


def runner():
    asyncio.run(start())


if __name__ == '__main__':
    watchfiles.run_process('.', target='main.runner')
