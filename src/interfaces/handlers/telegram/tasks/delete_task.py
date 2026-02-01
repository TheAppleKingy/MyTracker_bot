from aiogram import types, F, Router
from aiogram.fsm.context import FSMContext
from dishka.integrations.aiogram import FromDishka

from src.interfaces.presentators.telegram.keyboards.shared import back_kb, main_page_kb, yes_or_no_kb
from src.application.interfaces.clients import BackendClientInterface
from src.interfaces.handlers.telegram.errors import HandlerError
from src.logger import logger

delete_task_router = Router(name='Delete tasks')


@delete_task_router.callback_query(F.data.startswith('delete_task_'))
async def delete_task(
    event: types.CallbackQuery,
    context: FSMContext,
    backend: FromDishka[BackendClientInterface]
):
    await event.answer()
    await context.clear()
    data = event.data.split("_")[2:]
    task_id = int(data[0])
    parent_id: int | None = eval(data[1])
    ok, is_active = await backend.check_task_active(event.from_user.username, task_id)
    if not ok:
        raise HandlerError(is_active, kb=main_page_kb())
    status = "active" if is_active else "finished"
    await context.update_data(task_id=task_id, parent_id=parent_id, deleted_status=status)
    return await event.message.answer(
        text=f"<b>Are you sure? All subtasks will be deleted too</b>",
        parse_mode="HTML",
        reply_markup=yes_or_no_kb(
            "delete_yes_task", f"get_task_{task_id}")
    )


@delete_task_router.callback_query(F.data == 'delete_yes_task')
async def delete_task_yes(
    event: types.CallbackQuery,
    context: FSMContext,
    backend: FromDishka[BackendClientInterface]
):
    await event.answer()
    data = await context.get_data()
    await context.clear()
    ok, res = await backend.delete_task(event.from_user.username, data["task_id"])
    kb = back_kb(f"get_subtasks_{data["deleted_status"]}_{data["parent_id"]}_1" if data.get(
        "parent_id") else f"get_tasks_{data["deleted_status"]}_1")
    if not ok:
        raise HandlerError(res, kb=kb)
    await event.message.answer("<b>Task deleted</b>", reply_markup=kb, parse_mode="HTML")
