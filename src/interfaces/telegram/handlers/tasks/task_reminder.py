from datetime import datetime, timezone

from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram3_calendar import simple_cal_callback, SimpleCalendar as calendar   # type: ignore
from dishka.integrations.aiogram import FromDishka

from src.interfaces.telegram.keyboards.times import kalendar_kb, remind_time_kb
from src.interfaces.telegram.keyboards.shared import back_kb
from src.application.interfaces.clients import BackendClientInterface
from src.application.interfaces import StorageInterface
from src.application.interfaces.services import NotifyServiceInterface


reminder_router = Router(name="Reminder")


@reminder_router.callback_query(F.data.startswith('add_reminder_'))
async def add_reminder(
    cq: types.CallbackQuery,
    state: FSMContext,
    storage: FromDishka[StorageInterface],
    backend: FromDishka[BackendClientInterface]
):
    await cq.answer()
    await state.clear()
    task_id = int(cq.data.split('_')[-1])   # type: ignore
    _, task = await backend.get_task(cq.from_user.username, task_id)   # type: ignore
    user_tz = await storage.get_tz(cq.from_user.username)   # type: ignore
    await state.update_data(
        task_id=task.id,  # type: ignore
        task_deadline_local=task.deadline.astimezone(user_tz).isoformat(),  # type: ignore
        task_title=task.title  # type: ignore
    )
    now_local = datetime.now(timezone.utc).astimezone(user_tz)
    return await cq.message.answer(  # type: ignore
        text="Choose remind date",
        reply_markup=await kalendar_kb(now_local.year, now_local.month)
    )


@reminder_router.callback_query(simple_cal_callback.filter())
async def ask_remind_date(
    cq: types.CallbackQuery,
    callback_data: simple_cal_callback,
    state: FSMContext,
    storage: FromDishka[StorageInterface],

):
    await cq.answer()
    selected, date = await calendar().process_selection(cq, callback_data)
    if not selected:
        return
    data = await state.get_data()
    user_tz = await storage.get_tz(cq.from_user.username)
    current_deadline_local = datetime.fromisoformat(data.get("task_deadline_local"))
    selected_local: datetime = date.replace(tzinfo=user_tz)
    now_local = datetime.now(timezone.utc).astimezone(user_tz)
    if current_deadline_local < selected_local:
        return await cq.message.edit_text(
            f"<b>Cannot set reminder after deadline day</b>",
            reply_markup=await kalendar_kb(), parse_mode='HTML'
        )
    if now_local.date() > selected_local.date():
        return await cq.message.edit_text(
            f"<b>Cannot set reminder earlier than today</b>",
            reply_markup=await kalendar_kb(), parse_mode='HTML'
        )
    await state.update_data(remind_date=date.isoformat())
    remained_time = current_deadline_local - now_local
    if remained_time.seconds < 10:
        await state.clear()
        return await cq.message.answer(
            "<b>Deadline over less than a 10 seconds!</b>",
            reply_markup=back_kb(f"get_task_{data.get("task_id")}"),
            parse_mode='HTML'
        )
    await cq.message.edit_text(f'Choosen date for remind is {selected_local.strftime('%d.%m.%Y')}')
    return await cq.message.answer("Choose time", reply_markup=remind_time_kb(current_deadline_local, date))


@reminder_router.callback_query(F.data.startswith('set_remind_hour_'))
async def set_remind_hour(
    cq: types.CallbackQuery,
    state: FSMContext,
    storage: FromDishka[StorageInterface],
    notify_service: FromDishka[NotifyServiceInterface]
):
    await cq.answer()
    remind_hour = int(cq.data.split('_')[-1])
    data = await state.get_data()
    user_tz = storage.get_tz(cq.from_user.username)
    remind_datetime_utc = datetime.fromisoformat(data.get('remind_date')).replace(
        hour=remind_hour, tzinfo=user_tz).astimezone(timezone.utc)
    current_deadline_local = datetime.fromisoformat(data.get("task_deadline_local"))
    remained_time = current_deadline_local.astimezone(timezone.utc) - remind_datetime_utc
    remained_time_str = ''
    if remained_time.days >= 1:
        remained_time_str += f'{remained_time.days}d {remained_time.seconds // 3600 - 24*remained_time.days}h'
    else:
        remained_time_str += f'{remained_time.seconds//3600} hours'
    msg = f'Task "{data.get("task_title")}..." is waiting! Deadline over ' + remained_time
    notify_service.send_notify(msg, cq.message.chat.id, remind_datetime_utc)
    await state.clear()
    await cq.message.edit_text(f'Chosen time for remind is {'0'+str(remind_hour) if remind_hour <= 9 else remind_hour}h:00m', reply_markup=None)
    await cq.message.answer("Done!", reply_markup=back_kb(f"get_task_{data.get("task_id")}"))
