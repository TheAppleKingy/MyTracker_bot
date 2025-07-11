from aiogram import types, F
from aiogram.fsm.context import FSMContext

from keyboards.tasks import root_list_kb, subtasks_list_kb, create_task_kb
from api.client import BackendClient
from api.schemas import Task
from ..routers import task_router


@task_router.callback_query(F.data == 'get_task_all')
async def my_tasks(cq: types.CallbackQuery, state: FSMContext):
    await cq.answer()
    client = BackendClient(cq.from_user.username)
    response = await client.get_my_tasks()
    if response.json == []:
        return cq.message.answer("You have no tasks", reply_markup=create_task_kb())
    tasks = [Task(**task_data) for task_data in response.json]
    await cq.message.answer("Choose task", reply_markup=root_list_kb(tasks))


@task_router.callback_query(F.data.startswith('get_task_'))
async def task_info(cq: types.CallbackQuery, state: FSMContext):
    await cq.answer()
    task_id = cq.data.split('_')[-1]
    client = BackendClient(cq.from_user.username)
    response = await client.get_my_task(task_id)
    task = Task(**response.json)
    await cq.message.answer(str(task), reply_markup=subtasks_list_kb(task.subtasks))
