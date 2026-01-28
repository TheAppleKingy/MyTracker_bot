from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from dishka.integrations.aiogram import FromDishka

from src.application.interfaces.clients import BackendClientInterface
from src.interfaces.telegram.keyboards.shared import main_page_kb

registration_router = Router(name="Registration")


@registration_router.callback_query(F.data == 'register')
async def register(cq: types.CallbackQuery, state: FSMContext, backend: FromDishka[BackendClientInterface]):
    await cq.answer()
    await backend.register(cq.from_user.username)
    await cq.message.edit_text(text='Registration confirmed! Success! Now you have to define your time zone in settings', reply_markup=main_page_kb())
