from datetime import datetime, timezone

from aiogram import types, F, Router
from aiogram.fsm.context import FSMContext

from keyboards.tasks import add_subtask_kb
from api.client import BackendClient
from api.schemas import TaskCreatedSchema
from api.redis_client import get_user_tz, set_user_tz_val
from states.task_states import CreateTaskStates


create_task_router = Router(name='Create tasks')


@create_task_router.callback_query(F.data == 'create_task')
async def ask_title(cq: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await cq.answer()
    await cq.message.answer("Send me task title")
    await state.set_state(CreateTaskStates.waiting_title)


@create_task_router.message(CreateTaskStates.waiting_title)
async def ask_description(message: types.Message, state: FSMContext):
    await state.update_data({'title': message.text})
    await message.answer('Send me description of task')
    await state.set_state(CreateTaskStates.waiting_description)


@create_task_router.message(CreateTaskStates.waiting_description)
async def check_tz(message: types.Message, state: FSMContext):
    await state.update_data({'description': message.text})
    tz = await get_user_tz(message.from_user.username)
    if not tz:
        await message.answer("Send me your time zone in format +7 | -2 | 0(utc from)")
        await state.set_state(CreateTaskStates.waiting_tz)
        return
    await message.answer('Send me deadline for task in format dd.mm.yy hh:mm')
    await state.set_state(CreateTaskStates.waiting_deadline)


@create_task_router.message(CreateTaskStates.waiting_tz)
async def setup_tz(message: types.Message, state: FSMContext):
    await set_user_tz_val(message.text, message.from_user.username)
    await message.answer('Send me deadline for task in format dd.mm.yy hh:mm')
    await state.set_state(CreateTaskStates.waiting_deadline)


@create_task_router.message(CreateTaskStates.waiting_deadline)
async def ask_deadline(message: types.Message, state: FSMContext):
    user_tz = await get_user_tz(message.from_user.username)
    deadline_utc = datetime.strptime(message.text, '%d.%m.%Y %H:%M').replace(
        tzinfo=user_tz).astimezone(timezone.utc)
    creation_date_utc = datetime.now(timezone.utc)
    await state.update_data(deadline=deadline_utc.isoformat(), creation_date=creation_date_utc.isoformat())
    data = await state.get_data()
    await state.clear()
    client = BackendClient(message.from_user.username)
    response = await client.create_task(**data)
    task = TaskCreatedSchema(**response.json)
    await message.answer(task.show_to_message(user_tz), reply_markup=add_subtask_kb(task.id))
    await state.clear()


@create_task_router.callback_query(F.data.startswith('create_subtask_'))
async def create_subtask(cq: types.CallbackQuery, state: FSMContext):
    await cq.answer()
    parent_id = int(cq.data.split('_')[-1])
    await state.update_data(task_id=parent_id)
    await cq.message.answer('Send me subtask title')
    await state.set_state(CreateTaskStates.waiting_title)
