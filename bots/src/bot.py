import config

from redis.asyncio import from_url
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage

from handlers.routers import (
    start_router,
    auth_router,
    task_router
)
from middleware import BackendResponseMiddleware


bot = Bot(config.TOKEN)
redis = from_url(config.REDIS_URL, decode_responses=True)
redis_storage = RedisStorage(redis)
dispatcher = Dispatcher(storage=redis_storage)
dispatcher.message.middleware(BackendResponseMiddleware())
dispatcher.callback_query.middleware(BackendResponseMiddleware())


async def start():
    dispatcher.include_routers(
        start_router, auth_router, task_router)
    await dispatcher.start_polling(bot)
