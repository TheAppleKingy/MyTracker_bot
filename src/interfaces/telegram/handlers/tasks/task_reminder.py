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
from src.interfaces.telegram.states import RemindState
from src.interfaces.telegram.handlers.errors import HandlerError
from src.interfaces.presentators.time import show_timedelta_verbose

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
    user_tz = await storage.get_tz(cq.from_user.username)   # type: ignore
    now_local = datetime.now(timezone.utc).astimezone(user_tz)
    ok, res = await backend.get_task(cq.from_user.username, task_id)
    if not ok:
        raise HandlerError(res, kb=back_kb(f"main_page"))
    await state.set_state(RemindState.waiting_remind_date)
    await state.update_data(deadline=res.deadline.isoformat(), task_id=task_id, task_title=res.title)
    return await cq.message.answer(  # type: ignore
        text="<b>Choose remind date</b>",
        reply_markup=await kalendar_kb(now_local.year, now_local.month),
        parse_mode="HTML"
    )


@reminder_router.callback_query(simple_cal_callback.filter(), RemindState.waiting_remind_date)
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
    current_deadline_local = datetime.fromisoformat(data["deadline"]).astimezone(user_tz)
    selected_local: datetime = date.replace(tzinfo=user_tz)
    now_local = datetime.now(timezone.utc).astimezone(user_tz)
    if current_deadline_local < selected_local:
        return await cq.message.edit_text(
            f"<b>Cannot set reminder after deadline day</b>",
            reply_markup=await kalendar_kb(now_local.year, now_local.month), parse_mode='HTML'
        )
    if now_local.date() > selected_local.date():
        return await cq.message.edit_text(
            f"<b>Cannot set reminder earlier than today</b>",
            reply_markup=await kalendar_kb(now_local.year, now_local.month), parse_mode='HTML'
        )
    await state.update_data(remind_date=date.isoformat())
    remained_time = current_deadline_local - now_local
    if remained_time.seconds < 10:
        await state.clear()
        return await cq.message.answer(
            "<b>Deadline over less than a 10 seconds!</b>",
            reply_markup=back_kb(f"get_task_{data["task_id"]}"),
            parse_mode='HTML'
        )
    await cq.message.edit_text(
        text=f'<b>Choosen date for remind is {selected_local.strftime('%d.%m.%Y')}</b>',
        reply_markup=None,
        parse_mode="HTML"
    )
    return await cq.message.answer(
        text="<b>Choose time</b>",
        reply_markup=remind_time_kb(current_deadline_local, date),
        parse_mode="HTML"
    )


@reminder_router.callback_query(F.data.startswith('set_remind_hour_'))
async def set_remind_hour(
    cq: types.CallbackQuery,
    state: FSMContext,
    storage: FromDishka[StorageInterface],
    notify_service: FromDishka[NotifyServiceInterface]
):
    await cq.answer()
    suf = cq.data.split("_")[-1]
    if suf == "manually":
        await state.set_state(RemindState.waiting_remind_time)
        msg = await cq.message.edit_text(
            text=f"<b>Enter time in format HH:MM</b>",
            reply_markup=None,
            parse_mode="HTML"
        )
        await state.update_data(last_message=msg.message_id)
        return
    data = await state.get_data()
    hour = int(suf)
    user_tz = storage.get_tz(cq.from_user.username)
    remind_datetime_utc = datetime.fromisoformat(data.get('remind_date')).replace(
        hour=hour, tzinfo=user_tz).astimezone(timezone.utc)
    current_deadline_local = datetime.fromisoformat(data["deadline"]).astimezone(user_tz)
    remained_time = current_deadline_local.astimezone(timezone.utc) - remind_datetime_utc
    remained_time_str = show_timedelta_verbose(remained_time)
    msg = f'<b>Task "{data.get["task_title"]}" is waiting! Deadline over ' + remained_time_str + "</b>"
    notify_service.send_notify(msg, cq.message.chat.id, remind_datetime_utc)
    await state.clear()
    await cq.message.edit_text(
        text=f'<b>Chosen time for remind is {'0'+str(hour) if hour <= 9 else hour}h:00m</b>',
        reply_markup=None,
        parse_mode="HTML"
    )
    await cq.message.answer("<b>Done!</b>", reply_markup=back_kb(f"get_task_{data["task_id"]}"))
