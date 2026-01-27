from aiogram import types, Router
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from aiogram.filters.command import Command

from src.interfaces.telegram.keyboards.settings import settings_list_kb
from src.interfaces.telegram.handlers.rollback import rollback

settings_router = Router(name='Settings')


@settings_router.message(Command("settings"), StateFilter("*"))
async def cmd_settings(message: types.Message, state: FSMContext):
    await rollback(message, state)
    return await message.answer("Choose term", reply_markup=settings_list_kb())
