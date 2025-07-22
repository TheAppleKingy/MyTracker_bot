from aiogram import types, F, Router
from aiogram.fsm.context import FSMContext

from keyboards.tasks import root_list_kb, for_task_info_kb, create_task_kb
from api.client import BackendClient
from api.schemas import TaskViewSchema
from api.redis_client import get_user_tz


show_task_router = Router(name='Show tasks')


@show_task_router.callback_query(F.data == 'get_task_all')
async def my_tasks(cq: types.CallbackQuery, state: FSMContext):
    await cq.answer()
    client = BackendClient(cq.from_user.username)
    response = await client.get_my_tasks()
    if response.json == []:
        return cq.message.answer("You have no tasks", reply_markup=create_task_kb())
    tasks = [TaskViewSchema(**task_data) for task_data in response.json]
    await cq.message.answer("Choose task", reply_markup=root_list_kb(tasks))


@show_task_router.callback_query(F.data.startswith('get_task_'))
async def task_info(cq: types.CallbackQuery, state: FSMContext):
    await cq.answer()
    task_id = int(cq.data.split('_')[-1])
    client = BackendClient(cq.from_user.username)
    response = await client.get_my_task(task_id)
    task = TaskViewSchema(**response.json)
    user_tz = await get_user_tz(cq.from_user.username)
    await cq.message.answer(task.show_to_message(user_tz), reply_markup=for_task_info_kb(task))
