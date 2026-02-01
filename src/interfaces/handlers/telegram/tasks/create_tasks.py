from datetime import datetime, timezone

from aiogram import types, F, Router, Bot
from aiogram.fsm.context import FSMContext
from aiogram3_calendar import simple_cal_callback, SimpleCalendar as calendar
from dishka.integrations.aiogram import FromDishka

from src.interfaces.presentators.telegram.keyboards.times import deadline_time_kb, kalendar_kb
from src.interfaces.presentators.telegram.keyboards.shared import back_kb
from src.interfaces.presentators.telegram.keyboards.shared import main_page_kb
from src.interfaces.presentators.telegram.keyboards.tasks import under_task_info_kb
from src.interfaces.handlers.telegram.states.task import CreateTaskStates
from src.interfaces.adapters.time import validate_time
from src.interfaces.presentators.task import show_task_data
from src.application.interfaces.clients import BackendClientInterface
from src.application.interfaces import StorageInterface
from src.interfaces.handlers.telegram.errors import HandlerError
from src.logger import logger


create_task_router = Router(name='Create tasks')


@create_task_router.callback_query(F.data == 'create_task')
async def ask_title(event: types.CallbackQuery, context: FSMContext):
    await event.answer()
    await context.clear()
    await context.set_state(CreateTaskStates.waiting_title)
    return await event.message.answer("<b>Send me task title</b>", parse_mode="HTML")


@create_task_router.message(CreateTaskStates.waiting_title)
async def ask_description(event: types.Message, context: FSMContext):
    await context.update_data({'title': event.text})
    await context.set_state(CreateTaskStates.waiting_description)
    return await event.answer('<b>Send me description of task</b>', parse_mode="HTML")


@create_task_router.message(CreateTaskStates.waiting_description)
async def check_tz(
    event: types.Message,
    context: FSMContext,
    storage: FromDishka[StorageInterface]
):
    await context.update_data({'description': event.text})
    await context.set_state(CreateTaskStates.waiting_deadline_date)
    user_tz = await storage.get_tz(event.from_user.username)
    if not user_tz:
        raise HandlerError(
            "You have to define your timezone in settings",
            kb=main_page_kb()
        )
    now_local = datetime.now(timezone.utc).astimezone(user_tz)
    return await event.answer(
        '<b>Choose deadline date</b>',
        reply_markup=await kalendar_kb(now_local.year, now_local.month),
        parse_mode="HTML"
    )


@create_task_router.callback_query(simple_cal_callback.filter(), CreateTaskStates.waiting_deadline_date)
async def ask_deadline_date(
    event: types.CallbackQuery,
    callback_data: simple_cal_callback,
    context: FSMContext,
    storage: FromDishka[StorageInterface]
):
    await event.answer()
    selected, date = await calendar().process_selection(event, callback_data)
    if not selected:
        return
    user_tz = await storage.get_tz(event.from_user.username)
    selected_local: datetime = date.replace(tzinfo=user_tz)
    now_local = datetime.now(timezone.utc).astimezone(user_tz)
    if selected_local.date() < now_local.date():
        return await event.message.edit_text(
            text='<b>Deadline date cannot be earlier than today</b>',
            reply_markup=await kalendar_kb(now_local.year, now_local.month),
            parse_mode="HTML"
        )
    await context.update_data(deadline=selected_local.isoformat())
    await event.message.edit_text(
        f"<b>Choosen deadline date is {selected_local.strftime('%d.%m.%Y')}</b>",
        reply_markup=None,
        parse_mode="HTML"
    )
    return await event.message.answer(
        text="<b>Select deadline time</b>",
        reply_markup=deadline_time_kb(selected_local),
        parse_mode="HTML"
    )


@create_task_router.callback_query(F.data.startswith('set_deadline_hour_'))
async def set_deadline_time(
    event: types.CallbackQuery,
    context: FSMContext,
    storage: FromDishka[StorageInterface],
    backend: FromDishka[BackendClientInterface]
):
    suf = event.data.split("_")[-1]
    if suf == "manually":
        await context.set_state(CreateTaskStates.waiting_deadline_time)
        msg = await event.message.edit_text(
            text=f"<b>Enter time in format HH:MM</b>",
            reply_markup=None,
            parse_mode="HTML"
        )
        await context.update_data(last_message=msg.message_id)
        return
    hour = int(suf)
    data = await context.get_data()
    await context.clear()
    user_tz = await storage.get_tz(event.from_user.username)
    data["deadline"] = datetime.fromisoformat(data["deadline"]).replace(hour=hour)
    await event.message.edit_text(
        f"<b>Choosen deadline time is {data["deadline"].strftime("%Hh:%Mm")}</b>",
        reply_markup=None,
        parse_mode="HTML"
    )
    ok, res = await backend.create_task(event.from_user.username, **data)
    if not ok:
        raise HandlerError(res, kb=back_kb(f"get_task_{data["parent_id"] if data.get("parent_id") else "main_page"}"))
    return await event.message.answer(
        text=show_task_data(res, user_tz),
        reply_markup=under_task_info_kb(res),
        parse_mode="HTML"
    )


@create_task_router.message(CreateTaskStates.waiting_deadline_time)
async def set_task_deadline_manually(
    event: types.Message,
    context: FSMContext,
    backend: FromDishka[BackendClientInterface],
    bot: FromDishka[Bot]
):
    deadline_time = validate_time(event.text)
    data = await context.get_data()
    data["deadline"] = datetime.fromisoformat(data['deadline']).replace(
        hour=deadline_time.hour, minute=deadline_time.minute)
    now_local = datetime.now(timezone.utc).astimezone(data["deadline"].tzinfo)
    if now_local > data["deadline"]:
        raise HandlerError("Deadline time cannot be earlier than now", clear_state=False, add_last_message=True)
    await context.clear()
    await bot.edit_message_text(
        chat_id=event.chat.id,
        message_id=data.pop("last_message"),
        text=f"<b>Choosen deadline time is {data['deadline'].strftime("%Hh:%Mm")}</b>",
        reply_markup=None,
        parse_mode="HTML"
    )
    ok, res = await backend.create_task(event.from_user.username, **data)
    if not ok:
        raise HandlerError(res, kb=back_kb(f"get_task_{data["parent_id"] if data.get("parent_id") else "main_page"}"))
    return await event.answer(
        text=show_task_data(res, data["deadline"].tzinfo),
        reply_markup=under_task_info_kb(res),
        parse_mode="HTML"
    )


@create_task_router.callback_query(F.data.startswith('create_subtask_'))
async def create_subtask(event: types.CallbackQuery, context: FSMContext):
    await event.answer()
    await context.clear()
    parent_id = int(event.data.split('_')[-1])
    await context.update_data(parent_id=parent_id)
    await context.set_state(CreateTaskStates.waiting_title)
    return await event.message.answer('<b>Send me subtask title</b>', parse_mode="HTML")
