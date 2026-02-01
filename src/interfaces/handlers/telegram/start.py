from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.filters.command import CommandStart
from dishka.integrations.aiogram import FromDishka

from src.application.interfaces.clients import BackendClientInterface
from src.interfaces.presentators.telegram.keyboards.shared import main_kb
from src.interfaces.presentators.telegram.keyboards.auth import register_kb
from src.logger import logger
from .errors import HandlerError


start_router = Router(name='Start')


@start_router.message(CommandStart())
async def cmd_start(event: types.Message, context: FSMContext,  backend: FromDishka[BackendClientInterface]):
    await context.clear()
    ok, registered = await backend.check_registered(event.from_user.username)  # type: ignore
    if not ok:
        raise HandlerError("Service unaccessible. Try later")
    if not registered:
        return await event.answer(f"<b>Hello! Register in service</b>", reply_markup=register_kb(), parse_mode="HTML")
    return await event.answer(f"<b>Hello there!</b>", reply_markup=main_kb(), parse_mode="HTML")


@start_router.callback_query(F.data == "main_page")
async def main(event: types.CallbackQuery, context: FSMContext):
    await event.answer()
    await context.clear()
    return await event.message.answer(   # type: ignore
        text=f"<b>Choose term</b>",
        reply_markup=main_kb(),
        parse_mode="HTML"
    )
