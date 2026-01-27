from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from dishka.integrations.aiogram import FromDishka

from src.application.interfaces.api_client import BackendClientInterface
from src.interfaces.telegram.keyboards.settings import settings_kb
from src.interfaces.telegram.keyboards.tasks import my_tasks_button

registration_router = Router(name="Registration")


@registration_router.callback_query(F.data == 'register')
async def register(cq: types.CallbackQuery, state: FSMContext, backend: FromDishka[BackendClientInterface]):
    await cq.answer()
    result = await backend.register(cq.from_user.username)
    if result:
        return await cq.message.answer(result, reply_markup=None)
    await cq.message.answer("Success! Now you have to define your time zone in settings", reply_markup=settings_kb())
    await cq.message.edit_text(text='Registration confirmed!', reply_markup=my_tasks_button())
