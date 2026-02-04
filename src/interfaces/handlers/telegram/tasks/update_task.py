from datetime import datetime, timezone

from aiogram import types, F, Router, Bot
from aiogram.fsm.context import FSMContext
from aiogram3_calendar import SimpleCalendar as calendar, simple_cal_callback  # type: ignore
from dishka.integrations.aiogram import FromDishka, AiogramMiddlewareData

from src.interfaces.presentators.telegram.keyboards.tasks import update_task_terms_kb, under_task_info_kb
from src.interfaces.presentators.telegram.keyboards.times import kalendar_kb, deadline_time_kb
from src.interfaces.presentators.telegram.keyboards.shared import back_kb, yes_or_no_kb
from src.interfaces.presentators.task import show_task_data
from src.interfaces.adapters.time import validate_time
from src.application.interfaces.clients import BackendClientInterface
from src.application.interfaces import AsyncStorageInterface
from src.interfaces.handlers.telegram.states import UpdateTaskStates
from src.interfaces.handlers.telegram.errors import HandlerError
from .shared import ChangeDeadline, FinishTask, ForceFinishTask


update_task_router = Router(name='Update tasks')


@update_task_router.callback_query(F.data.startswith('update_task_'))
async def choose_field(event: types.CallbackQuery, context: FSMContext):
    await event.answer()
    await context.clear()
    task_id = int(event.data.split('_')[-1])
    await context.update_data(updating_task=task_id)
    return await event.message.answer(
        text="<b>Choose what do you desire to change</b>",
        reply_markup=update_task_terms_kb(task_id),
        parse_mode="HTML"
    )


@update_task_router.callback_query(F.data.startswith('update_text_'))
async def ask_enter_value(
    event: types.CallbackQuery,
    context: FSMContext,
):
    await event.answer()
    field = event.data.split("_")[-1]
    await context.set_state(UpdateTaskStates.waiting_text_data)
    await context.update_data(updating_field=field)
    return await event.message.edit_text(text=f"<b>Enter new {field}</b>", reply_markup=None, parse_mode="HTML")


@update_task_router.message(UpdateTaskStates.waiting_text_data)
async def change_task_text_field(
    event: types.Message,
    context: FSMContext,
    backend: FromDishka[BackendClientInterface],
    storage: FromDishka[AsyncStorageInterface]
):
    data = await context.get_data()
    await context.clear()
    new_value = event.text
    to_update = {data["updating_field"]: new_value}
    ok, res = await backend.update_task(event.from_user.username, data["updating_task"], **to_update)
    if not ok:
        raise HandlerError(res, kb=back_kb(f"get_task_{data["updating_task"]}"))
    user_tz = await storage.get_tz(event.from_user.username)
    return await event.answer(
        text=show_task_data(res, user_tz), reply_markup=under_task_info_kb(res), parse_mode="HTML")


@update_task_router.callback_query(F.data == "update_deadline")
async def ask_enter_new_deadline_date(
    event: types.CallbackQuery,
    context: FSMContext,
    storage: FromDishka[AsyncStorageInterface]
):
    await event.answer()
    user_tz = await storage.get_tz(event.from_user.username)
    now_local = datetime.now(timezone.utc).astimezone(user_tz)
    await context.set_state(UpdateTaskStates.waiting_deadline_date)
    return await event.message.answer(
        text=f"<b>Choose new deadline date</b>",
        reply_markup=await kalendar_kb(now_local.year, now_local.month),
        parse_mode="HTML"
    )


@update_task_router.callback_query(simple_cal_callback.filter(), UpdateTaskStates.waiting_deadline_date)
async def ask_enter_new_deadline_time(
    event: types.CallbackQuery,
    callback_data: simple_cal_callback,
    context: FSMContext,
    storage: FromDishka[AsyncStorageInterface]
):
    selected, date = await calendar().process_selection(event, callback_data)
    if not selected:
        return
    user_tz = await storage.get_tz(event.from_user.username)
    now_local = datetime.now(timezone.utc).astimezone(user_tz)
    selected_local: datetime = date.replace(tzinfo=user_tz)
    if now_local.date() > selected_local.date():
        return await event.message.edit_text(
            f'<b>New deadline date cannot be earlier than today</b>',
            reply_markup=await kalendar_kb(now_local.year, now_local.month),
            parse_mode='HTML'
        )
    await context.update_data(deadline=selected_local.isoformat())
    await event.message.edit_text(
        text=f"<b>Choosen new deadline date is {selected_local.strftime('%d.%m.%Y')}</b>",
        reply_markup=None,
        parse_mode="HTML"
    )
    return await event.message.answer(
        text="<b>Select new deadline time</b>",
        reply_markup=deadline_time_kb(selected_local, for_update=True),
        parse_mode="HTML"
    )


# @update_task_router.callback_query(F.data.startswith("update_deadline_hour_"))
# async def change_task_deadline(
#     event: types.CallbackQuery,
#     context: FSMContext,
#     backend: FromDishka[BackendClientInterface],
#     storage: FromDishka[AsyncStorageInterface],
#     notify_service: FromDishka[NotifyServiceInterface]
# ):
#     suf = event.data.split("_")[-1]
#     if suf == "manually":
#         await context.set_state(UpdateTaskStates.waiting_deadline_time)
#         msg = await event.message.edit_text(
#             text=f"<b>Enter time in format HH:MM</b>",
#             reply_markup=None,
#             parse_mode="HTML"
#         )
#         await context.update_data(last_message=msg.message_id)
#         return
#     hour = int(suf)
#     data = await context.get_data()
#     await context.clear()
#     new_deadline = datetime.fromisoformat(data['deadline']).replace(hour=hour)
#     await event.message.edit_text(
#         f"<b>Choosen new deadline time is {new_deadline.strftime("%Hh:%Mm")}</b>",
#         reply_markup=None,
#         parse_mode="HTML"
#     )
#     ok, res = await backend.update_task(event.from_user.username, data["updating_task"], deadline=new_deadline)
#     if not ok:
#         raise HandlerError(res, kb=back_kb(f"get_task_{data["updating_task"]}"))
#     reminders_map = await storage.get_reminders_tab(event.from_user.username, data["updating_task"])
#     if reminders_map:
#         to_revoke = []
#         for reminder_id, eta in reminders_map.items():
#             if eta > new_deadline.astimezone(timezone.utc):
#                 to_revoke.append(reminder_id)
#                 notify_service.revoke_reminder(reminder_id)
#         await storage.delete_reminders(event.from_user.username, to_revoke, data["updating_task"])
#     return await event.message.answer(
#         text=show_task_data(res, new_deadline.tzinfo),
#         reply_markup=under_task_info_kb(res),
#         parse_mode="HTML"
#     )


# @update_task_router.message(UpdateTaskStates.waiting_deadline_time)
# async def change_task_deadline_manually(
#     event: types.Message,
#     context: FSMContext,
#     backend: FromDishka[BackendClientInterface],
#     bot: FromDishka[Bot],
#     storage: FromDishka[AsyncStorageInterface],
#     notify_service: FromDishka[NotifyServiceInterface]
# ):
#     new_time = validate_time(event.text)
#     data = await context.get_data()
#     new_deadline = datetime.fromisoformat(data['deadline']).replace(
#         hour=new_time.hour, minute=new_time.minute)
#     now_local = datetime.now(timezone.utc).astimezone(new_deadline.tzinfo)
#     if now_local > new_deadline:
#         raise HandlerError("New deadline time cannot be earlier than now", clear_state=False, add_last_message=True)
#     await context.clear()
#     await bot.edit_message_text(
#         chat_id=event.chat.id,
#         message_id=data["last_message"],
#         text=f"<b>Choosen new deadline time is {new_time.strftime("%Hh:%Mm")}</b>",
#         reply_markup=None,
#         parse_mode="HTML"
#     )
#     ok, res = await backend.update_task(event.from_user.username, data["updating_task"], deadline=new_deadline)
#     if not ok:
#         raise HandlerError(res, kb=back_kb(f"get_task_{data["updating_task"]}"))
#     reminders_map = await storage.get_reminders_tab(event.from_user.username, data["updating_task"])
#     if reminders_map:
#         to_revoke = []
#         for reminder_id, eta in reminders_map.items():
#             if eta > new_deadline.astimezone(timezone.utc):
#                 to_revoke.append(reminder_id)
#                 notify_service.revoke_reminder(reminder_id)
#         await storage.delete_reminders(event.from_user.username, to_revoke, data["updating_task"])
#     return await event.answer(
#         text=show_task_data(res, new_deadline.tzinfo),
#         reply_markup=under_task_info_kb(res),
#         parse_mode="HTML"
#     )


@update_task_router.callback_query(F.data.startswith("update_deadline_hour_"))
async def change_task_deadline(
    event: types.CallbackQuery,
    context: FSMContext,
    use_case: FromDishka[ChangeDeadline],
):
    suf = event.data.split("_")[-1]
    if suf == "manually":
        await context.set_state(UpdateTaskStates.waiting_deadline_time)
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
    new_deadline = datetime.fromisoformat(data['deadline']).replace(hour=hour)
    await event.message.edit_text(
        f"<b>Choosen new deadline time is {new_deadline.strftime("%Hh:%Mm")}</b>",
        reply_markup=None,
        parse_mode="HTML"
    )
    res = await use_case.execute(event.from_user.username, new_deadline, data["updating_task"])
    return await event.message.answer(
        text=show_task_data(res, new_deadline.tzinfo),
        reply_markup=under_task_info_kb(res),
        parse_mode="HTML"
    )


@update_task_router.message(UpdateTaskStates.waiting_deadline_time)
async def change_task_deadline_manually(
    event: types.Message,
    context: FSMContext,
    bot: FromDishka[Bot],
    use_case: FromDishka[ChangeDeadline]
):
    new_time = validate_time(event.text)
    data = await context.get_data()
    new_deadline = datetime.fromisoformat(data['deadline']).replace(
        hour=new_time.hour, minute=new_time.minute)
    now_local = datetime.now(timezone.utc).astimezone(new_deadline.tzinfo)
    if now_local > new_deadline:
        raise HandlerError("New deadline time cannot be earlier than now", clear_state=False, add_last_message=True)
    await context.clear()
    await bot.edit_message_text(
        chat_id=event.chat.id,
        message_id=data["last_message"],
        text=f"<b>Choosen new deadline time is {new_time.strftime("%Hh:%Mm")}</b>",
        reply_markup=None,
        parse_mode="HTML"
    )
    res = await use_case.execute(event.from_user.username, new_deadline, data["updating_task"])
    return await event.answer(
        text=show_task_data(res, new_deadline.tzinfo),
        reply_markup=under_task_info_kb(res),
        parse_mode="HTML"
    )


@update_task_router.callback_query(F.data.startswith("finish_task_"))
async def finish_task(
    event: types.CallbackQuery,
    context: FSMContext,
):
    await event.answer()
    await context.clear()
    task_id = int(event.data.split("_")[-1])
    await context.update_data(finishing_task=task_id)
    return await event.message.answer(
        text=f"<b>Do you want to finish all subtasks forcely?</b>",
        reply_markup=yes_or_no_kb("force_finish_task", "soft_finish_task"),
        parse_mode="HTML"
    )


@update_task_router.callback_query(F.data == ("force_finish_task"))
async def force_finish_task(
    event: types.CallbackQuery,
    context: FSMContext,
    use_case: FromDishka[ForceFinishTask]
):
    await event.answer()
    data = await context.get_data()
    await context.clear()
    await use_case.execute(event.from_user.username, data["finishing_task"])
    return await event.message.edit_text(
        text=f"<b>Task and all subtasks finished</b>",
        reply_markup=back_kb(f"get_task_{data["finishing_task"]}"),
        parse_mode="HTML"
    )


@update_task_router.callback_query(F.data == ("soft_finish_task"))
async def soft_finish_task(
    event: types.CallbackQuery,
    context: FSMContext,
    use_case: FromDishka[FinishTask]
):
    await event.answer()
    data = await context.get_data()
    await context.clear()
    await use_case.execute(event.from_user.username, data["finishing_task"])
    return await event.message.edit_text(
        text=f"<b>Task finished</b>",
        reply_markup=back_kb(f"get_task_{data["finishing_task"]}"),
        parse_mode="HTML"
    )
