from aiogram import types, Router
from aiogram.filters.command import Command

from keyboards.settings import settings_list_kb

settings_router = Router(name='Settings')


@settings_router.message(Command("settings"))
async def cmd_settings(message: types.Message):
    return await message.answer("Choose term", reply_markup=settings_list_kb())
