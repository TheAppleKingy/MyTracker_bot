from aiogram import types, F, Router
from aiogram.fsm.context import FSMContext

from keyboards.tasks import get_my_tasks_kb
from api.client import BackendClient


delete_task_router = Router(name='Delete tasks')


@delete_task_router.callback_query(F.data.startswith('delete_task_'))
async def delete_task(cq: types.CallbackQuery, state: FSMContext):
    await cq.answer()
    task_id = int(cq.data.split('_')[-1])
    client = BackendClient(cq.from_user.username)
    await client.delete_task(task_id)
    await cq.message.answer("Task deleted", reply_markup=get_my_tasks_kb())
