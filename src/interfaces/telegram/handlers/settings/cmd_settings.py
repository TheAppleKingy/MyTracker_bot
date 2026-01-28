from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext

from src.interfaces.telegram.keyboards.settings import settings_list_kb
from src.interfaces.telegram.handlers.rollback import rollback

settings_router = Router(name='Settings')


@settings_router.callback_query(F.data == "settings")
async def cmd_settings(cq: types.CallbackQuery, state: FSMContext):
    # await rollback(message, state)
    await cq.answer()
    return await cq.message.answer("Choose term", reply_markup=settings_list_kb())
