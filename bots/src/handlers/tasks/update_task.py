from datetime import datetime, timezone

from aiogram import types, F, Router
from aiogram.fsm.context import FSMContext

from keyboards.tasks import for_task_update_kb, for_task_info_kb, back_kb
from api.client import BackendClient
from api.schemas import TaskViewSchema
from api.redis_client import get_user_tz
from states.task_states import UpdateTaskStates


update_task_router = Router(name='Update tasks')


@update_task_router.callback_query(F.data.startswith('update_task_'))
async def choose_update_term(cq: types.CallbackQuery, state: FSMContext):
    await cq.answer()
    task_id = int(cq.data.split('_')[-1])
    await state.update_data(updating_task=task_id)
    await cq.message.answer(text="Choose what do u want to change", reply_markup=for_task_update_kb(task_id))


@update_task_router.callback_query(F.data.startswith('change_'))
async def ask_enter_value(cq: types.CallbackQuery, state: FSMContext):
    await cq.answer()
    updating_field = cq.data.split('_')[-1]
    expected_state = UpdateTaskStates.resolve_state(updating_field)
    additional = ' in format dd.mm.YYYY HH:MM'
    msg = f"Enter new {updating_field}"
    if updating_field == 'deadline':
        msg += additional
    await cq.message.answer(msg)
    await state.set_state(expected_state)


@update_task_router.message(UpdateTaskStates.waiting_title)
async def change_task_title(message: types.Message, state: FSMContext):
    task_id = (await state.get_data()).get('updating_task')
    new_title = message.text
    client = BackendClient(message.from_user.username)
    response = await client.update_task(task_id=task_id, title=new_title)
    task = TaskViewSchema(**response.json)
    user_tz = await get_user_tz(message.from_user.username)
    await message.answer(task.show_to_message(user_tz), reply_markup=for_task_info_kb(task), parse_mode='HTML')
    await state.clear()


@update_task_router.message(UpdateTaskStates.waiting_description)
async def change_task_description(message: types.Message, state: FSMContext):
    task_id = (await state.get_data()).get('updating_task')
    new_description = message.text
    client = BackendClient(message.from_user.username)
    response = await client.update_task(task_id=task_id, description=new_description)
    task = TaskViewSchema(**response.json)
    user_tz = await get_user_tz(message.from_user.username)
    await message.answer(task.show_to_message(user_tz), reply_markup=for_task_info_kb(task), parse_mode='HTML')
    await state.clear()


@update_task_router.message(UpdateTaskStates.waiting_deadline)
async def change_task_deadline(message: types.Message, state: FSMContext):
    task_id = (await state.get_data()).get('updating_task')
    new_deadline = message.text
    user_tz = await get_user_tz(message.from_user.username)
    formatted = datetime.strptime(new_deadline, "%d.%m.%Y %H:%M").replace(
        tzinfo=user_tz).astimezone(timezone.utc)
    client = BackendClient(message.from_user.username)
    response = await client.update_task(task_id=task_id, deadline=formatted.isoformat())
    task = TaskViewSchema(**response.json)
    await message.answer(task.show_to_message(user_tz), reply_markup=for_task_info_kb(task), parse_mode='HTML')
    await state.clear()


@update_task_router.callback_query(F.data.startswith('mark_done_'))
async def mark_task_as_done(cq: types.CallbackQuery, state: FSMContext):
    await cq.answer()
    task_id = int(cq.data.split('_')[-1])
    client = BackendClient(cq.from_user.username)
    await client.finish_task(task_id)
    await cq.message.answer("Task done!", reply_markup=back_kb(task_id))
    await state.clear()
