from aiogram import types, F, Router
from aiogram.fsm.context import FSMContext
from dishka.integrations.aiogram import FromDishka

from src.application.interfaces.clients import BackendClientInterface, TimezoneClientInterface
from src.application.interfaces import StorageInterface
from src.interfaces.telegram.keyboards.tasks import under_task_info_kb, no_tasks_kb, root_active_tasks_kb
from src.interfaces.presentators.task import show_task_data


show_task_router = Router(name='Show tasks')


@show_task_router.callback_query(F.data == 'get_active_tasks')
async def active_tasks(
    cq: types.CallbackQuery,
    state: FSMContext,
    backend: FromDishka[BackendClientInterface]
):
    await cq.answer()
    tasks = await backend.get_active_tasks(cq.from_user.username)
    if not tasks:
        return await cq.message.answer("You have no active tasks", reply_markup=no_tasks_kb())
    await cq.message.answer("Your active tasks", reply_markup=root_active_tasks_kb(tasks))


@show_task_router.callback_query(F.data == 'get_finished_tasks')
async def finished_tasks(
    cq: types.CallbackQuery,
    state: FSMContext,
    backend: FromDishka[BackendClientInterface]
):
    await cq.answer()
    tasks = await backend.get_finished_tasks(cq.from_user.username)
    if not tasks:
        return await cq.message.answer("You have no finished tasks", reply_markup=no_tasks_kb())
    await cq.message.answer("Your finished tasks", reply_markup=root_active_tasks_kb(tasks))


@show_task_router.callback_query(F.data.startswith('get_task_'))
async def task_info(
    cq: types.CallbackQuery,
    state: FSMContext,
    backend: FromDishka[BackendClientInterface],
    storage: FromDishka[StorageInterface]
):
    await cq.answer()
    await state.clear()
    task_id = int(cq.data.split('_')[-1])
    task = await backend.get_task(cq.from_user.username, task_id)
    user_tz = await storage.get_tz(cq.from_user.username)
    return await cq.message.answer(
        show_task_data(task, user_tz),
        reply_markup=under_task_info_kb(task),
        parse_mode='HTML'
    )
