from aiogram import types, F, Router
from aiogram.fsm.context import FSMContext
from dishka.integrations.aiogram import FromDishka

from src.application.interfaces.clients import BackendClientInterface
from src.application.interfaces import AsyncStorageInterface
from src.interfaces.presentators.telegram.keyboards.tasks import under_task_info_kb, no_tasks_kb, page_tasks_kb, no_subtasks_kb
from src.interfaces.presentators.telegram.keyboards.shared import main_page_kb, back_kb
from src.interfaces.presentators.task import show_task_data
from src.logger import logger
from src.interfaces.handlers.telegram.errors import HandlerError

show_task_router = Router(name='Show tasks')


@show_task_router.callback_query(F.data.startswith('get_tasks_'))
async def tasks_page(
    event: types.CallbackQuery,
    context: FSMContext,
    backend: FromDishka[BackendClientInterface]
):
    await event.answer()
    data = event.data.split("_")[2:]
    status, page = data[0], int(data[1])
    if data[-1] == "fromnavigation":
        answer = event.message.edit_text
    else:
        answer = event.message.answer
    ok, resp = await backend.get_tasks(event.from_user.username, status, page=page)
    if not ok:
        return HandlerError(resp, kb=main_page_kb())
    prev, next_, tasks = resp
    if not tasks:
        return await event.message.answer(
            text=f"<b>You have no {status} tasks</b>",
            parse_mode="HTML",
            reply_markup=no_tasks_kb()
        )
    return await answer(
        f"<b>Your {status} tasks</b>",
        reply_markup=page_tasks_kb(tasks, status, prev_page=prev, next_page=next_),
        parse_mode="HTML"
    )


@show_task_router.callback_query(F.data.startswith("get_subtasks_"))
async def subtasks_page(
    event: types.CallbackQuery,
    context: FSMContext,
    backend: FromDishka[BackendClientInterface],
):
    await event.answer()
    data = event.data.split("_")[2:]
    status, parent_id, page = data[0], int(data[1]), int(data[2])
    if data[-1] == "fromnavigation":
        answer = event.message.edit_text
    else:
        answer = event.message.answer
    ok, resp = await backend.get_subtasks(event.from_user.username, status, parent_id, page=page)
    if not ok:
        raise HandlerError(resp, kb=back_kb(f"get_task_{parent_id}"))
    prev, next_, tasks = resp
    if not tasks:
        return await event.message.answer(
            text=f"<b>You have no {status} subtasks</b>",
            parse_mode="HTML",
            reply_markup=no_subtasks_kb(parent_id)
        )
    return await answer(
        text=f"<b>Your {status} subtasks</b>",
        parse_mode="HTML",
        reply_markup=page_tasks_kb(tasks, status, prev_page=prev, next_page=next_, parent_id=parent_id)
    )


@show_task_router.callback_query(F.data.startswith('get_task_'))
async def task_info(
    event: types.CallbackQuery,
    context: FSMContext,
    backend: FromDishka[BackendClientInterface],
    storage: FromDishka[AsyncStorageInterface]
):
    await event.answer()
    await context.clear()
    task_id = int(event.data.split('_')[-1])
    ok, task = await backend.get_task(event.from_user.username, task_id)
    if not ok:
        raise HandlerError(task, kb=main_page_kb())
    user_tz = await storage.get_tz(event.from_user.username)
    return await event.message.answer(
        text=show_task_data(task, user_tz),
        reply_markup=under_task_info_kb(task),
        parse_mode='HTML'
    )
