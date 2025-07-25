from datetime import datetime, timezone

from aiogram import types, F, Router
from aiogram.fsm.context import FSMContext
from aiogram3_calendar import simple_cal_callback, SimpleCalendar as calendar

from keyboards.tasks import for_task_info_kb, kalendar_kb, reminders_time_kb, yes_or_no_kb
from api.client import BackendClient
from api.schemas import TaskViewSchema
from api.redis_client import get_user_tz, set_user_tz_val
from states.task_states import CreateTaskStates, RemindTimeCountState
from tasks.notify import notify


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
    client = BackendClient(message.from_user.username)
    response = await client.create_task(**data)
    task = TaskViewSchema(**response.json)
    await message.answer("Task created! Do you want i will remind you about deadline?", reply_markup=yes_or_no_kb('add_reminder', f'get_task_{task.id}'))
    await state.update_data(task=task.model_dump_json())


@create_task_router.callback_query(F.data == 'add_reminder')
async def add_reminder(cq: types.CallbackQuery, state: FSMContext):
    await cq.answer()
    await cq.message.answer("Choose remind date", reply_markup=await kalendar_kb())
    await state.update_data(remind_times=[])


@create_task_router.callback_query(simple_cal_callback.filter())
async def ask_remind_time(cq: types.CallbackQuery, callback_data: simple_cal_callback, state: FSMContext):
    await cq.answer()
    selected, date = await calendar().process_selection(cq, callback_data)
    if not selected:
        return
    data = await state.get_data()
    task = TaskViewSchema.model_validate_json(data.get('task'))
    user_tz = await get_user_tz(cq.from_user.username)
    deadline_local = task.deadline.astimezone(user_tz)
    remind_times = data.get('remind_times')
    remind_times.append(date.strftime('%d.%m.%Y'))
    await state.update_data(remind_times=remind_times)
    await cq.message.answer("Choose time", reply_markup=reminders_time_kb(deadline_local.hour))


@create_task_router.callback_query(F.data.startswith('set_remind_hour_'))
async def set_remind_hour(cq: types.CallbackQuery, state: FSMContext):
    await cq.answer()
    remind_hour = int(cq.data.split('_')[-1])
    data = await state.get_data()
    remind_times = data.get('remind_times')
    current_remind_date = datetime.strptime(remind_times[-1], '%d.%m.%Y')
    current_remind_datetime = current_remind_date.replace(hour=remind_hour)
    user_tz = await get_user_tz(cq.from_user.username)
    remind_datetime_utc = current_remind_datetime.replace(
        tzinfo=user_tz).astimezone(timezone.utc)
    task = TaskViewSchema.model_validate_json(data.get('task'))
    deadline_utc = task.deadline
    remained_time = deadline_utc - remind_datetime_utc
    remained_time_str = ''
    print(remind_datetime_utc)
    if remained_time.days >= 1:
        remained_time_str += f'{remained_time.days} days'
    else:
        remained_time_str += f'{remained_time.seconds//3600}'
    notify.apply_async(args=[task.title, remained_time_str,
                       cq.message.chat.id], eta=remind_datetime_utc)
    await state.clear()
    await cq.message.answer("Done! ")


@create_task_router.callback_query(F.data.startswith('create_subtask_'))
async def create_subtask(cq: types.CallbackQuery, state: FSMContext):
    await cq.answer()
    parent_id = int(cq.data.split('_')[-1])
    await state.update_data(task_id=parent_id)
    await cq.message.answer('Send me subtask title')
    await state.set_state(CreateTaskStates.waiting_title)
