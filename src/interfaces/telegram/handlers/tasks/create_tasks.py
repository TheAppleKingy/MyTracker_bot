from datetime import datetime, timezone

from aiogram import types, F, Router, Bot
from aiogram.fsm.context import FSMContext
from aiogram3_calendar import simple_cal_callback, SimpleCalendar as calendar
from dishka.integrations.aiogram import FromDishka

from src.interfaces.telegram.keyboards.times import deadline_time_kb, kalendar_kb
from src.interfaces.telegram.keyboards.shared import back_kb
from src.interfaces.telegram.keyboards.shared import main_page_kb
from src.interfaces.telegram.keyboards.tasks import under_task_info_kb
from src.interfaces.telegram.states.task import CreateTaskStates
from src.interfaces.presentators.task import show_task_data
from src.application.interfaces.clients import BackendClientInterface
from src.application.interfaces import StorageInterface
from src.interfaces.telegram.handlers.errors import HandlerError


create_task_router = Router(name='Create tasks')


@create_task_router.callback_query(F.data == 'create_task')
async def ask_title(cq: types.CallbackQuery, state: FSMContext):
    await cq.answer()
    await state.clear()
    await state.set_state(CreateTaskStates.waiting_title)
    return await cq.message.answer("<b>Send me task title</b>", parse_mode="HTML")


@create_task_router.message(CreateTaskStates.waiting_title)
async def ask_description(message: types.Message, state: FSMContext):
    await state.update_data({'title': message.text})
    await state.set_state(CreateTaskStates.waiting_description)
    return await message.answer('<b>Send me description of task</b>', parse_mode="HTML")


@create_task_router.message(CreateTaskStates.waiting_description)
async def check_tz(
    message: types.Message,
    state: FSMContext,
    storage: FromDishka[StorageInterface]
):
    await state.update_data({'description': message.text})
    await state.set_state(CreateTaskStates.waiting_deadline_date)
    user_tz = await storage.get_tz(message.from_user.username)
    if not user_tz:
        raise HandlerError(
            "You have to define your timezone in settings",
            kb=main_page_kb()
        )
    now_local = datetime.now(timezone.utc).astimezone(user_tz)
    return await message.answer(
        '<b>Choose deadline date</b>',
        reply_markup=await kalendar_kb(now_local.year, now_local.month),
        parse_mode="HTML"
    )


@create_task_router.callback_query(simple_cal_callback.filter(), CreateTaskStates.waiting_deadline_date)
async def ask_deadline_date(
    cq: types.CallbackQuery,
    callback_data: simple_cal_callback,
    state: FSMContext,
    storage: FromDishka[StorageInterface]
):
    await cq.answer()
    selected, date = await calendar().process_selection(cq, callback_data)
    if not selected:
        return
    user_tz = await storage.get_tz(cq.from_user.username)
    selected_local: datetime = date.replace(tzinfo=user_tz)
    now_local = datetime.now(timezone.utc).astimezone(user_tz)
    if selected_local.date() < now_local.date():
        return await cq.message.edit_text(
            text='<b>Deadline date cannot be earlier than today</b>',
            reply_markup=await kalendar_kb(now_local.year, now_local.month),
            parse_mode="HTML"
        )
    await state.update_data(deadline=selected_local.isoformat())
    await cq.message.edit_text(
        f"<b>Choosen deadline date is {selected_local.strftime('%d.%m.%Y')}</b>",
        reply_markup=None,
        parse_mode="HTML"
    )
    return await cq.message.answer(
        text="<b>Select deadline time</b>",
        reply_markup=deadline_time_kb(user_tz, date),
        parse_mode="HTML"
    )


@create_task_router.callback_query(F.data.startswith('set_deadline_hour_'))
async def set_deadline_time(
    cq: types.CallbackQuery,
    state: FSMContext,
    storage: FromDishka[StorageInterface],
    backend: FromDishka[BackendClientInterface]
):
    suf = cq.data.split("_")[-1]
    if suf == "manually":
        await state.set_state(CreateTaskStates.waiting_deadline_time)
        msg = await cq.message.edit_text(
            text=f"<b>Enter time in format HH:MM</b>",
            reply_markup=None,
            parse_mode="HTML"
        )
        await state.update_data(last_message=msg.message_id)
        return
    hour = int(suf)
    data = await state.get_data()
    await state.clear()
    user_tz = await storage.get_tz(cq.from_user.username)
    data["deadline"] = datetime.fromisoformat(data['deadline']).replace(hour=hour)
    await cq.message.edit_text(
        f"<b>Choosen deadline time is {'0' + hour if hour <= 9 else hour}h:00m</b>",
        reply_markup=None,
        parse_mode="HTML"
    )
    ok, res = await backend.create_task(cq.from_user.username, **data)
    if not ok:
        raise HandlerError(res, kb=back_kb(f"get_task_{data["parent_id"] if data.get("parent_id") else "main_page"}"))
    return await cq.message.answer(
        text=show_task_data(res, user_tz),
        reply_markup=under_task_info_kb(res),
        parse_mode="HTML"
    )


@create_task_router.message(CreateTaskStates.waiting_deadline_time)
async def set_task_deadline_manually(
    message: types.Message,
    state: FSMContext,
    backend: FromDishka[BackendClientInterface],
    bot: FromDishka[Bot]
):
    try:
        new_time = datetime.strptime(message.text, "%H:%M").time()
    except ValueError:
        raise HandlerError("Invalid time format. Try again", clear_state=False)
    data = await state.get_data()
    await state.clear()
    data["deadline"] = datetime.fromisoformat(data['deadline']).replace(hour=new_time.hour, minute=new_time.minute)
    now_local = datetime.now(timezone.utc).astimezone(data["deadline"].tzinfo)
    if now_local > data["deadline"]:
        raise HandlerError("Deadline time cannot be earlier than now", clear_state=False)
    await bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=data.pop("last_message"),
        text=f"<b>Choosen deadline time is {new_time.strftime("%Hh:%Mm")}</b>",
        reply_markup=None,
        parse_mode="HTML"
    )
    ok, res = await backend.create_task(message.from_user.username, **data)
    if not ok:
        raise HandlerError(res, kb=back_kb(f"get_task_{data["parent_id"] if data.get("parent_id") else "main_page"}"))
    return await message.answer(
        text=show_task_data(res, data["deadline"].tzinfo),
        reply_markup=under_task_info_kb(res),
        parse_mode="HTML"
    )


@create_task_router.callback_query(F.data.startswith('create_subtask_'))
async def create_subtask(cq: types.CallbackQuery, state: FSMContext):
    await cq.answer()
    await state.clear()
    parent_id = int(cq.data.split('_')[-1])
    await state.update_data(parent_id=parent_id)
    await state.set_state(CreateTaskStates.waiting_title)
    return await cq.message.answer('<b>Send me subtask title</b>', parse_mode="HTML")
