from datetime import datetime, timezone

from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext

from aiogram3_calendar import simple_cal_callback, SimpleCalendar as calendar

from keyboards.tasks import kalendar_kb, back_kb, remind_time_kb

from api.redis_client import get_user_tz
from api.schemas import TaskViewSchema
from tasks.notify import notify
from api.client import BackendClient


reminder_router = Router(name="Reminder")


@reminder_router.callback_query(F.data.startswith('add_reminder_'))
async def add_reminder(cq: types.CallbackQuery, state: FSMContext):
    await cq.answer()
    task_id = int(cq.data.split('_')[-1])
    client = BackendClient(cq.from_user.username)
    response = await client.get_my_task(task_id)
    response.json.pop('subtasks')
    task = TaskViewSchema(**response.json)
    await state.update_data(task=task.model_dump_json())
    await cq.message.answer("Choose remind date", reply_markup=await kalendar_kb())


@reminder_router.callback_query(simple_cal_callback.filter())
async def ask_remind_time(cq: types.CallbackQuery, callback_data: simple_cal_callback, state: FSMContext):
    await cq.answer()
    selected, date = await calendar().process_selection(cq, callback_data)
    if not selected:
        return
    data = await state.get_data()
    task = TaskViewSchema.model_validate_json(data.get('task'))
    user_tz = await get_user_tz(cq.from_user.username)
    deadline_local = task.deadline.astimezone(user_tz)
    await state.update_data(remind_date=date.isoformat())
    current_time_local = datetime.now(timezone.utc).astimezone(user_tz)
    remained_time = deadline_local - current_time_local
    if remained_time.seconds < 3600:
        await cq.message.answer("Deadline over less than a hour!", reply_markup=back_kb(task.id))
        await state.clear()
        return
    await cq.message.answer("Choose time", reply_markup=remind_time_kb(deadline_local, date))


@reminder_router.callback_query(F.data.startswith('set_remind_hour_'))
async def set_remind_hour(cq: types.CallbackQuery, state: FSMContext):
    await cq.answer()
    remind_hour = int(cq.data.split('_')[-1])
    data = await state.get_data()
    user_tz = await get_user_tz(cq.from_user.username)
    task = TaskViewSchema.model_validate_json(data.get('task'))
    remind_datetime_utc = datetime.fromisoformat(data.get('remind_date')).replace(
        hour=remind_hour, tzinfo=user_tz).astimezone(timezone.utc)
    remained_time = task.deadline - remind_datetime_utc
    remained_time_str = ''
    if remained_time.days >= 1:
        remained_time_str += f'{remained_time.days} days'
    else:
        remained_time_str += f'{remained_time.seconds//3600} hours'
    notify.apply_async(args=[task.title, remained_time_str,
                       cq.message.chat.id], eta=remind_datetime_utc)
    await state.clear()
    await cq.message.answer("Done!", reply_markup=back_kb(task.id))
