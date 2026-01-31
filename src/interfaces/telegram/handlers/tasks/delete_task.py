from aiogram import types, F, Router
from aiogram.fsm.context import FSMContext
from dishka.integrations.aiogram import FromDishka

from src.interfaces.telegram.keyboards.shared import back_kb, main_page_kb, yes_or_no_kb
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
    await state.clear()
    data = cq.data.split("_")[2:]
    task_id = int(data[0])
    parent_id: int | None = eval(data[1])
    status = "active" if await backend.check_task_active(cq.from_user.username, task_id) else "finished"
    await state.update_data(task_id=task_id, parent_id=parent_id, deleted_status=status)
    return await cq.message.answer(
        text=f"<b>Are you sure? All subtasks will be deleted too</b>",
        parse_mode="HTML",
        reply_markup=yes_or_no_kb(
            "delete_yes_task", f"get_task_{task_id}")
    )


@delete_task_router.callback_query(F.data == 'delete_yes_task')
async def delete_task_yes(
    cq: types.CallbackQuery,
    state: FSMContext,
    backend: FromDishka[BackendClientInterface]
):
    await cq.answer()
    data = await state.get_data()
    await state.clear()
    ok, res = await backend.delete_task(cq.from_user.username, data["task_id"])
    kb = back_kb(f"get_subtasks_{data["deleted_status"]}_{data["parent_id"]}_1" if data.get(
        "parent_id") else f"get_tasks_{data["deleted_status"]}_1")
    if not ok:
        raise HandlerError(res, kb=kb)
    await cq.message.answer("<b>Task deleted</b>", reply_markup=kb, parse_mode="HTML")
