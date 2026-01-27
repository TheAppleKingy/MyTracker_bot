from aiogram import types, Router
from aiogram.filters.command import CommandStart
from dishka.integrations.aiogram import FromDishka

from application.interfaces.clients.backend import BackendClientInterface
from src.interfaces.telegram.keyboards.tasks import get_my_tasks_kb
from src.interfaces.telegram.keyboards.auth import get_start_kb


start_router = Router(name='Start')


@start_router.message(CommandStart())
async def cmd_start(message: types.Message, backend: FromDishka[BackendClientInterface]):
    if await backend.check_registered(message.from_user.username):
        return await message.answer("Hello! Register in service", reply_markup=get_start_kb())
    return await message.answer("Hello there! Choice motion", reply_markup=get_my_tasks_kb())
