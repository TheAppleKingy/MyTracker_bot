from datetime import datetime, timezone

from aiogram import Router, types, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram3_calendar import simple_cal_callback, SimpleCalendar as calendar   # type: ignore
from dishka.integrations.aiogram import FromDishka

from src.interfaces.presentators.telegram.keyboards.times import kalendar_kb, remind_time_kb
from src.interfaces.presentators.telegram.keyboards.shared import back_kb
from src.application.interfaces.clients import BackendClientInterface
from src.application.interfaces import StorageInterface
from src.application.interfaces.services import NotifyServiceInterface
from src.interfaces.adapters.time import validate_time
from src.interfaces.handlers.telegram.states import RemindState
from src.interfaces.handlers.telegram.errors import HandlerError
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
    if res.deadline.astimezone(user_tz) < now_local:
        raise HandlerError(
            "Unable to set remind if deadline passed and task was not mark as finished. Change deadline",
            kb=back_kb(f"get_task_{task_id}")
        )
    await state.set_state(RemindState.waiting_remind_date)
    await state.update_data(deadline=res.deadline.astimezone(user_tz).isoformat(), task_id=task_id, task_title=res.title)
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

):
    await cq.answer()
    selected, date = await calendar().process_selection(cq, callback_data)
    if not selected:
        return
    data = await state.get_data()
    current_deadline_local = datetime.fromisoformat(data["deadline"])
    selected_local: datetime = date.replace(tzinfo=current_deadline_local.tzinfo)
    now_local = datetime.now(timezone.utc).astimezone(selected_local.tzinfo)
    if current_deadline_local.date() < selected_local.date():
        return await cq.message.edit_text(
            f"<b>Cannot set reminder after deadline day</b>",
            reply_markup=await kalendar_kb(now_local.year, now_local.month), parse_mode='HTML'
        )
    if now_local.date() > selected_local.date():
        return await cq.message.edit_text(
            f"<b>Cannot set reminder earlier than today</b>",
            reply_markup=await kalendar_kb(now_local.year, now_local.month), parse_mode='HTML'
        )
    await state.update_data(remind_date=selected_local.isoformat())
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
    remind_datetime_utc = datetime.fromisoformat(data['remind_date']).replace(hour=hour).astimezone(timezone.utc)
    current_deadline_local = datetime.fromisoformat(data["deadline"])
    remained_time = current_deadline_local.astimezone(timezone.utc) - remind_datetime_utc
    if remained_time.total_seconds() < 10:
        raise HandlerError(
            "Deadline less than over 10 seconds!",
            reply_markup=back_kb(f"get_task_{data["task_id"]}"),
        )
    await state.clear()
    remained_time_str = show_timedelta_verbose(remained_time)
    msg = f'<b>Task "{data["task_title"]}" is waiting! Deadline over ' + remained_time_str + "</b>"
    notify_service.send_notify(msg, cq.message.chat.id, remind_datetime_utc)
    await cq.message.edit_text(
        text=f'<b>Chosen time for remind is {remind_datetime_utc.astimezone(current_deadline_local.tzinfo).strftime("%Hh:%Mm")}</b>',
        reply_markup=None,
        parse_mode="HTML"
    )
    await cq.message.answer(
        text=f"<b>Done! Remind will be sent over {show_timedelta_verbose(remind_datetime_utc - datetime.now(timezone.utc))}</b>",
        reply_markup=back_kb(f"get_task_{data["task_id"]}"),
        parse_mode="HTML"
    )


@reminder_router.message(RemindState.waiting_remind_time)
async def set_remind_hour_manually(
    message: types.Message,
    state: FSMContext,
    notify_service: FromDishka[NotifyServiceInterface],
    bot: FromDishka[Bot],
    storage: FromDishka[StorageInterface]
):
    data = await state.get_data()
    remind_time = validate_time(message.text)
    remind_datetime_utc = datetime.fromisoformat(data['remind_date']).replace(
        hour=remind_time.hour,
        minute=remind_time.minute
    ).astimezone(timezone.utc)
    current_deadline_local = datetime.fromisoformat(data["deadline"])
    remained_time = current_deadline_local.astimezone(timezone.utc) - remind_datetime_utc
    if remained_time.total_seconds() < 0:
        raise HandlerError(
            "Unable to set remind after deadline",
            clear_state=False,
            add_last_message=True
        )
    if remained_time.total_seconds() < 10:
        raise HandlerError(
            "Deadline less than over 10 seconds!",
            reply_markup=back_kb(f"get_task_{data["task_id"]}"),
        )
    await state.clear()
    remained_time_str = show_timedelta_verbose(remained_time)
    msg = f'<b>Task "{data["task_title"]}" is waiting! Deadline over ' + remained_time_str + "</b>"
    notify_service.send_notify(msg, message.chat.id, remind_datetime_utc)

    await bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=data["last_message"],
        text=f'<b>Chosen time for remind is {remind_datetime_utc.astimezone(current_deadline_local.tzinfo).strftime("%Hh:%Mm")}</b>',
        reply_markup=None,
        parse_mode="HTML"
    )
    return await message.answer(
        text=f"<b>Done! Remind will be sent over {show_timedelta_verbose(remind_datetime_utc - datetime.now(timezone.utc))}</b>",
        reply_markup=back_kb(f"get_task_{data["task_id"]}"),
        parse_mode="HTML"
    )
