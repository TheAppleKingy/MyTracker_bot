from datetime import datetime, timezone

from aiogram import types, F, Router
from aiogram.fsm.context import FSMContext
from aiogram3_calendar import simple_cal_callback, SimpleCalendar as calendar

from keyboards.tasks import for_task_info_kb, kalendar_kb, deadline_time_kb
from api.client import BackendClient
from api.schemas import TaskViewSchema
from api.redis_client import get_user_tz
from states.task_states import CreateTaskStates


create_task_router = Router(name='Create tasks')


@create_task_router.callback_query(F.data == 'create_task')
async def ask_title(cq: types.CallbackQuery, state: FSMContext):
    await cq.answer()
    await state.clear()
    await state.set_state(CreateTaskStates.waiting_title)
    return await cq.message.answer("Send me task title")


@create_task_router.message(CreateTaskStates.waiting_title)
async def ask_description(message: types.Message, state: FSMContext):
    await state.update_data({'title': message.text})
    await state.set_state(CreateTaskStates.waiting_description)
    return await message.answer('Send me description of task')


@create_task_router.message(CreateTaskStates.waiting_description)
async def check_tz(message: types.Message, state: FSMContext):
    await state.update_data({'description': message.text})
    await state.set_state(CreateTaskStates.waiting_deadline)
    return await message.answer('Choose deadline date', reply_markup=await kalendar_kb())


@create_task_router.callback_query(simple_cal_callback.filter(), CreateTaskStates.waiting_deadline)
async def ask_deadline_date(cq: types.CallbackQuery, callback_data: simple_cal_callback, state: FSMContext):
    await cq.answer()
    selected, date = await calendar().process_selection(cq, callback_data)
    if not selected:
        return
    creation_date_utc = datetime.now(timezone.utc)
    user_tz = await get_user_tz(cq.from_user.username)
    today_local = datetime.now(timezone.utc).astimezone(user_tz)
    selected_local: datetime = date.replace(tzinfo=user_tz)
    if today_local.date() > selected_local.date():
        await cq.message.edit_text(f'<b>Deadline date cannot be earlier than today</b>', reply_markup=await kalendar_kb(), parse_mode='HTML')
        return
    await state.update_data(deadline=date.isoformat(), creation_date=creation_date_utc.isoformat())
    await cq.message.edit_text(f"Chose deadline date is {selected_local.strftime('%Y-%m-%d')}", reply_markup=None)
    return await cq.message.answer("Select deadline time", reply_markup=deadline_time_kb(user_tz, date))


@create_task_router.callback_query(F.data.startswith('set_deadline_hour_'))
async def set_deadline_time(cq: types.CallbackQuery, state: FSMContext):
    await cq.message.edit_reply_markup(reply_markup=None)
    deadline_hour = int(cq.data.split('_')[-1])
    data = await state.get_data()
    await state.clear()
    user_tz = await get_user_tz(cq.from_user.username)
    deadline_utc = datetime.fromisoformat(data.get('deadline')).replace(
        hour=deadline_hour, tzinfo=user_tz).astimezone(timezone.utc)
    data.update({'deadline': deadline_utc.isoformat()})
    client = BackendClient(cq.from_user.username)
    data.pop('rollback_msg', None)
    response = await client.create_task(**data)
    task = TaskViewSchema(**response.json)
    await cq.message.edit_text(f"Chosen deadline time is {'0'+deadline_hour if deadline_hour <= 9 else deadline_hour}h:00m")
    await cq.message.answer(task.show_to_message(user_tz), reply_markup=for_task_info_kb(task), parse_mode='HTML')


@create_task_router.callback_query(F.data.startswith('create_subtask_'))
async def create_subtask(cq: types.CallbackQuery, state: FSMContext):
    await cq.answer()
    await state.clear()
    parent_id = int(cq.data.split('_')[-1])
    await state.update_data(task_id=parent_id)
    await state.set_state(CreateTaskStates.waiting_title)
    return await cq.message.answer('Send me subtask title')
