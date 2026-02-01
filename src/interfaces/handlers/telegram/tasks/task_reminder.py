from datetime import datetime, timezone

from aiogram import Router, types, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram3_calendar import simple_cal_callback, SimpleCalendar as calendar   # type: ignore
from dishka.integrations.aiogram import FromDishka

from src.interfaces.presentators.telegram.keyboards.times import kalendar_kb, remind_time_kb
from src.interfaces.presentators.telegram.keyboards.shared import back_kb
from src.interfaces.presentators.telegram.keyboards.tasks import reminders_kb, no_reminders_kb, under_reminder_kb
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
    event: types.CallbackQuery,
    context: FSMContext,
    storage: FromDishka[StorageInterface],
    backend: FromDishka[BackendClientInterface]
):
    await event.answer()
    await context.clear()
    task_id = int(event.data.split('_')[-1])   # type: ignore
    user_tz = await storage.get_tz(event.from_user.username)   # type: ignore
    now_local = datetime.now(timezone.utc).astimezone(user_tz)
    ok, res = await backend.get_task(event.from_user.username, task_id)
    if not ok:
        raise HandlerError(res, kb=back_kb(f"main_page"))
    if res.deadline.astimezone(user_tz) < now_local:
        raise HandlerError(
            "Unable to set remind if deadline passed and task was not mark as finished. Change deadline",
            kb=back_kb(f"get_task_{task_id}")
        )
    await context.set_state(RemindState.waiting_remind_date)
    await context.update_data(deadline=res.deadline.astimezone(user_tz).isoformat(), task_id=task_id, task_title=res.title)
    return await event.message.answer(  # type: ignore
        text="<b>Choose remind date</b>",
        reply_markup=await kalendar_kb(now_local.year, now_local.month),
        parse_mode="HTML"
    )


@reminder_router.callback_query(simple_cal_callback.filter(), RemindState.waiting_remind_date)
async def ask_remind_date(
    event: types.CallbackQuery,
    callback_data: simple_cal_callback,
    context: FSMContext,

):
    await event.answer()
    selected, date = await calendar().process_selection(event, callback_data)
    if not selected:
        return
    data = await context.get_data()
    current_deadline_local = datetime.fromisoformat(data["deadline"])
    selected_local: datetime = date.replace(tzinfo=current_deadline_local.tzinfo)
    now_local = datetime.now(timezone.utc).astimezone(selected_local.tzinfo)
    if current_deadline_local.date() < selected_local.date():
        return await event.message.edit_text(
            f"<b>Cannot set reminder after deadline day</b>",
            reply_markup=await kalendar_kb(now_local.year, now_local.month), parse_mode='HTML'
        )
    if now_local.date() > selected_local.date():
        return await event.message.edit_text(
            f"<b>Cannot set reminder earlier than today</b>",
            reply_markup=await kalendar_kb(now_local.year, now_local.month), parse_mode='HTML'
        )
    await context.update_data(remind_date=selected_local.isoformat())
    await event.message.edit_text(
        text=f'<b>Choosen date for remind is {selected_local.strftime('%d.%m.%Y')}</b>',
        reply_markup=None,
        parse_mode="HTML"
    )
    return await event.message.answer(
        text="<b>Choose time</b>",
        reply_markup=remind_time_kb(current_deadline_local, selected_local),
        parse_mode="HTML"
    )


@reminder_router.callback_query(F.data.startswith('set_remind_hour_'))
async def set_remind_hour(
    event: types.CallbackQuery,
    context: FSMContext,
    notify_service: FromDishka[NotifyServiceInterface],
    storage: FromDishka[StorageInterface]
):
    await event.answer()
    suf = event.data.split("_")[-1]
    if suf == "manually":
        await context.set_state(RemindState.waiting_remind_time)
        msg = await event.message.edit_text(
            text=f"<b>Enter time in format HH:MM</b>",
            reply_markup=None,
            parse_mode="HTML"
        )
        await context.update_data(last_message=msg.message_id)
        return
    data = await context.get_data()
    hour = int(suf)
    remind_datetime_utc = datetime.fromisoformat(data['remind_date']).replace(hour=hour).astimezone(timezone.utc)
    current_deadline_local = datetime.fromisoformat(data["deadline"])
    delta = current_deadline_local.astimezone(timezone.utc) - remind_datetime_utc
    await context.clear()
    delta_str = show_timedelta_verbose(delta)
    msg = f'<b>Task "{data["task_title"]}" is waiting! Deadline over ' + delta_str + "</b>"
    id_ = notify_service.send_notify(msg, event.chat.id, remind_datetime_utc)
    await storage.set_reminder(event.from_user.username, remind_datetime_utc, id_)
    await event.message.edit_text(
        text=f'<b>Chosen time for remind is {remind_datetime_utc.astimezone(current_deadline_local.tzinfo).strftime("%Hh:%Mm")}</b>',
        reply_markup=None,
        parse_mode="HTML"
    )
    await event.message.answer(
        text=f"<b>Done! Remind will be sent over {show_timedelta_verbose(remind_datetime_utc - datetime.now(timezone.utc))}</b>",
        reply_markup=back_kb(f"get_task_{data["task_id"]}"),
        parse_mode="HTML"
    )


@reminder_router.message(RemindState.waiting_remind_time)
async def set_remind_hour_manually(
    event: types.Message,
    context: FSMContext,
    notify_service: FromDishka[NotifyServiceInterface],
    bot: FromDishka[Bot],
    storage: FromDishka[StorageInterface]
):
    data = await context.get_data()
    remind_time = validate_time(event.text)
    remind_datetime_utc = datetime.fromisoformat(data['remind_date']).replace(
        hour=remind_time.hour,
        minute=remind_time.minute
    ).astimezone(timezone.utc)
    current_deadline_local = datetime.fromisoformat(data["deadline"])
    if remind_datetime_utc < datetime.now(timezone.utc):
        raise HandlerError("Unable to set reminder earlier than now", clear_state=False, add_last_message=True)
    delta = current_deadline_local.astimezone(timezone.utc) - remind_datetime_utc
    if delta.total_seconds() < 0:
        raise HandlerError(
            "Unable to set remind after deadline",
            clear_state=False,
            add_last_message=True
        )
    await context.clear()
    delta_str = show_timedelta_verbose(delta)
    msg = f'<b>Task "{data["task_title"]}" is waiting! Deadline over ' + delta_str + "</b>"
    id_ = notify_service.send_notify(msg, event.chat.id, remind_datetime_utc)
    await storage.set_reminder(event.from_user.username, remind_datetime_utc, id_)
    await bot.edit_message_text(
        chat_id=event.chat.id,
        message_id=data["last_message"],
        text=f'<b>Chosen time for remind is {remind_datetime_utc.astimezone(current_deadline_local.tzinfo).strftime("%Hh:%Mm")}</b>',
        reply_markup=None,
        parse_mode="HTML"
    )
    return await event.answer(
        text=f"<b>Done! Remind will be sent over {show_timedelta_verbose(remind_datetime_utc - datetime.now(timezone.utc))}</b>",
        reply_markup=back_kb(f"get_task_{data["task_id"]}"),
        parse_mode="HTML"
    )


@reminder_router.callback_query(F.data.startswith("get_reminders_"))
async def show_reminders(
    event: types.CallbackQuery,
    context: FSMContext,
    storage: FromDishka[StorageInterface]
):
    await event.answer()
    task_id = event.data.split("_")[-1]
    reminders_tab = await storage.get_reminders_tab(event.from_user.username)
    if not reminders_tab:
        raise HandlerError("No reminders found", kb=no_reminders_kb(task_id))
    user_tz = await storage.get_tz(event.from_user.username)
    await context.update_data(task_id=task_id)
    return await event.message.answer(
        text="<b>Current reminders</b>",
        reply_markup=reminders_kb(reminders_tab, task_id, user_tz),
        parse_mode="HTML"
    )


@reminder_router.callback_query(F.data.startswith("get_reminder_"))
async def show_reminder_actions(
    event: types.CallbackQuery,
    context: FSMContext,
    storage: FromDishka[StorageInterface]
):
    await event.answer()
    reminder_id = event.data.split("_")[-1]
    reminder: datetime = await storage.get_reminder(event.from_user.username, reminder_id)
    user_tz = await storage.get_tz(event.from_user.username)
    return await event.message.answer(
        text=f"<b>{reminder.astimezone(user_tz).strftime("%d.%m.%Y at %H:%M")}</b>",
        reply_markup=under_reminder_kb(reminder_id, await context.get_value("task_id")),
        parse_mode="HTML"
    )


@reminder_router.callback_query(F.data.startswith("delete_reminder_"))
async def delete_reminder(
    event: types.CallbackQuery,
    context: FSMContext,
    storage: FromDishka[StorageInterface],
    notify_service: FromDishka[NotifyServiceInterface]
):
    await event.answer()
    reminder_id = event.data.split("_")[-1]
    await storage.delete_reminder(event.from_user.username, reminder_id)
    notify_service.revoke_reminder(reminder_id)
    task_id = await context.get_value("task_id")
    await context.clear()
    return await event.message.answer(
        text="<b>Reminder deleted</b>",
        reply_markup=back_kb(f"get_reminders_{task_id}"),
        parse_mode="HTML"
    )
