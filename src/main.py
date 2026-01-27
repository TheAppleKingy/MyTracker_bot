import asyncio
import watchfiles

from aiogram import Bot, Dispatcher
from dishka.integrations.aiogram import setup_dishka

from src.interfaces.telegram.handlers import *
from src.container import container
from middleware import BackendResponseMiddleware, RollbackDetectorMiddleware


async def setup():
    dispatcher = await container.get(Dispatcher)
    dispatcher.include_routers(
        start_router,
        registration_router,
        show_task_router,
        create_task_router,
        update_task_router,
        reminder_router,
        settings_router,
        tz_router,
        delete_task_router
    )
    setup_dishka(container, dispatcher)
    bot = await container.get(Bot)
    await dispatcher.start_polling(bot)


def start():
    asyncio.run(setup())


if __name__ == '__main__':
    watchfiles.run_process('.', target='main.start')
