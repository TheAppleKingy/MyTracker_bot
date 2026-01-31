from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from dishka.integrations.aiogram import FromDishka

from src.application.interfaces.clients import BackendClientInterface
from src.interfaces.presentators.telegram.keyboards.shared import main_page_kb
from src.logger import logger

registration_router = Router(name="Registration")


@registration_router.callback_query(F.data == 'register')
async def register(cq: types.CallbackQuery, state: FSMContext, backend: FromDishka[BackendClientInterface]):
    await cq.answer()
    ok, data = await backend.register(cq.from_user.username)
    message = '<b>Registration confirmed succesfully! Now you have to define your time zone in settings</b>'
    kb = main_page_kb()
    if not ok:
        message = f"<b>{data}</b>"
        kb = None
    return await cq.message.edit_text(
        text=message,
        reply_markup=kb,
        parse_mode="HTML"
    )
