from aiogram import types, F, Router
from aiogram.fsm.context import FSMContext
from dishka.integrations.aiogram import FromDishka

from src.interfaces.telegram.keyboards.shared import main_page_kb
from src.application.interfaces.clients import BackendClientInterface

delete_task_router = Router(name='Delete tasks')


@delete_task_router.callback_query(F.data.startswith('delete_task_'))
async def delete_task(
    cq: types.CallbackQuery,
    state: FSMContext,
    backend: FromDishka[BackendClientInterface]
):
    await cq.answer()
    task_id = int(cq.data.split('_')[-1])
    await backend.delete_task(cq.from_user.username, task_id)
    await state.clear()
    await cq.message.answer("Task deleted", reply_markup=main_page_kb())
