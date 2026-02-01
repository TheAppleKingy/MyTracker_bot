from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext

from src.interfaces.presentators.telegram.keyboards.settings import settings_list_kb

settings_router = Router(name='Settings')


@settings_router.callback_query(F.data == "settings")
async def cmd_settings(event: types.CallbackQuery, context: FSMContext):
    # await rollback(message, context)
    await event.answer()
    return await event.message.answer(  # type: ignore
        "<b>Choose term</b>",
        reply_markup=settings_list_kb(),
        parse_mode="HTML"
    )
