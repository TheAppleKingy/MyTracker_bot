from aiogram import types, F, Router
from aiogram.fsm.context import FSMContext
from dishka.integrations.aiogram import FromDishka

from src.interfaces.telegram.keyboards.shared import back_kb, main_page_kb
from src.application.interfaces.clients import BackendClientInterface
from src.interfaces.telegram.handlers.errors import HandlerError

delete_task_router = Router(name='Delete tasks')


@delete_task_router.callback_query(F.data.startswith('delete_task_'))
async def delete_task(
    cq: types.CallbackQuery,
    state: FSMContext,
    backend: FromDishka[BackendClientInterface]
):
    await cq.answer()
    data = cq.data.split("_")[2:]
    task_id = int(data[0])
    parent_id: int | None = eval(data[1])
    ok, res = await backend.delete_task(cq.from_user.username, task_id)
    kb = back_kb(f"get_task_{parent_id}") if parent_id else main_page_kb()
    if not ok:
        raise HandlerError(res, kb=kb)
    await state.clear()
    await cq.message.answer("<b>Task deleted</b>", reply_markup=kb, parse_mode="HTML")
