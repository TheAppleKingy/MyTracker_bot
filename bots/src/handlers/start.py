from aiogram import types, Router
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.command import Command

from keyboards.auth import get_start_kb


start_router = Router(name='Start')


@start_router.message(Command("start"))
async def cmd_start(message: types.Message):
    return await message.answer("Hello there! Choice motion", reply_markup=get_start_kb())
