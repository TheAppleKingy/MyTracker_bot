from aiogram import types
from aiogram.fsm.context import FSMContext


async def rollback(trigger: types.CallbackQuery | types.Message, state: FSMContext):
    """this function let to stop handlers chain representing a user script"""
    data = await state.get_data()
    rollback_msg: int = data.pop('rollback_msg', None)
    if rollback_msg:
        await state.clear()
        resp = trigger.message if isinstance(
            trigger, types.CallbackQuery) else trigger
        await resp.bot.edit_message_text(
            'Operation aborted',
            reply_markup=None,
            chat_id=resp.chat.id,
            message_id=rollback_msg
        )
