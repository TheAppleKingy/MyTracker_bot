from aiogram import types, Router
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from aiogram.filters.command import Command

from keyboards.settings import settings_list_kb

from handlers.rollback import rollback

settings_router = Router(name='Settings')


@settings_router.message(Command("settings"), StateFilter("*"))
async def cmd_settings(message: types.Message, state: FSMContext):
    await rollback(message, state)
    return await message.answer("Choose term", reply_markup=settings_list_kb())
