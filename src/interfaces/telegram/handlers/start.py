from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.filters.command import CommandStart
from dishka.integrations.aiogram import FromDishka

from src.application.interfaces.clients import BackendClientInterface
from src.interfaces.telegram.keyboards.shared import main_kb
from src.interfaces.telegram.keyboards.auth import register_kb


start_router = Router(name='Start')


@start_router.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext,  backend: FromDishka[BackendClientInterface]):
    await state.clear()
    if not await backend.check_registered(message.from_user.username):
        return await message.answer("Hello! Register in service", reply_markup=register_kb())
    return await message.answer("Hello there!", reply_markup=main_kb())


@start_router.callback_query(F.data == "main_page")
async def main(cq: types.CallbackQuery, state: FSMContext):
    await cq.answer()
    await state.clear()
    return await cq.message.answer(text="Choose term", reply_markup=main_kb())
