from datetime import datetime, timezone

from aiogram import types, F, Router
from aiogram.fsm.context import FSMContext
from aiogram3_calendar import SimpleCalendar as calendar, simple_cal_callback

from keyboards.tasks import for_task_update_kb, for_task_info_kb, back_kb, kalendar_kb, deadline_time_kb
from api.client import BackendClient
from api.schemas import TaskViewSchema
from api.redis_client import get_user_tz
from states.task_states import UpdateTaskStates


update_task_router = Router(name='Update tasks')


@update_task_router.callback_query(F.data.startswith('update_task_'))
async def choose_update_term(cq: types.CallbackQuery, state: FSMContext):
    await cq.answer()
    await state.clear()
    task_id = int(cq.data.split('_')[-1])
    await state.update_data(updating_task=task_id)
    return await cq.message.answer(text="Choose what do u want to change", reply_markup=for_task_update_kb(task_id))


@update_task_router.callback_query(F.data.startswith('change_'))
async def ask_enter_value(cq: types.CallbackQuery, state: FSMContext):
    await cq.answer()
    await cq.message.edit_reply_markup(reply_markup=None)
    updating_field = cq.data.split('_')[-1]
    expected_state = UpdateTaskStates.resolve_state(updating_field)
    if updating_field == 'deadline':
        await state.set_state(UpdateTaskStates.waiting_deadline)
        return await cq.message.answer("Choose new deadline day", reply_markup=await kalendar_kb())
    msg = f"Enter new {updating_field}"
    await state.set_state(expected_state)
    return await cq.message.answer(msg)


@update_task_router.message(UpdateTaskStates.waiting_title)
async def change_task_title(message: types.Message, state: FSMContext):
    task_id = (await state.get_data()).get('updating_task')
    new_title = message.text
    client = BackendClient(message.from_user.username)
    response = await client.update_task(task_id=task_id, title=new_title)
    task = TaskViewSchema(**response.json)
    user_tz = await get_user_tz(message.from_user.username)
    await message.answer(task.show_to_message(user_tz), reply_markup=for_task_info_kb(task), parse_mode='HTML')
    await state.clear()


@update_task_router.message(UpdateTaskStates.waiting_description)
async def change_task_description(message: types.Message, state: FSMContext):
    task_id = (await state.get_data()).get('updating_task')
    new_description = message.text
    client = BackendClient(message.from_user.username)
    response = await client.update_task(task_id=task_id, description=new_description)
    task = TaskViewSchema(**response.json)
    user_tz = await get_user_tz(message.from_user.username)
    await message.answer(task.show_to_message(user_tz), reply_markup=for_task_info_kb(task), parse_mode='HTML')
    await state.clear()


@update_task_router.callback_query(simple_cal_callback.filter(), UpdateTaskStates.waiting_deadline)
async def change_task_deadline(cq: types.CallbackQuery, callback_data: simple_cal_callback, state: FSMContext):
    selected, date = await calendar().process_selection(cq, callback_data)
    if not selected:
        return
    user_tz = await get_user_tz(cq.from_user.username)
    today_local = datetime.now(timezone.utc).astimezone(user_tz)
    selected_local: datetime = date.replace(tzinfo=user_tz)
    if today_local.date() > selected_local.date():
        await cq.message.edit_text(f'<b>Deadline date cannot be earlier than today</b>', reply_markup=await kalendar_kb(), parse_mode='HTML')
        return
    await state.update_data(deadline=date.isoformat())
    await cq.message.edit_text(f"Chosen new deadline date is {selected_local.strftime('%Y-%m-%d')}", reply_markup=None)
    return await cq.message.answer("Select new deadline time", reply_markup=deadline_time_kb(user_tz, date, for_update=True))


@update_task_router.callback_query(F.data.startswith('update_deadline_hour_'))
async def set_new_deadline_hour(cq: types.CallbackQuery, state: FSMContext):
    await cq.message.edit_reply_markup(reply_markup=None)
    data = await state.get_data()
    task_id = data.get('updating_task')
    user_tz = await get_user_tz(cq.from_user.username)
    new_deadline_hour = int(cq.data.split('_')[-1])
    new_deadline_utc = datetime.fromisoformat(data.get('deadline')).replace(
        hour=new_deadline_hour, tzinfo=user_tz).astimezone(timezone.utc)
    client = BackendClient(cq.from_user.username)
    response = await client.update_task(task_id=task_id, deadline=new_deadline_utc.isoformat())
    task = TaskViewSchema(**response.json)
    await cq.message.edit_text(f"Chosen new deadline hour is {'0'+new_deadline_hour if new_deadline_hour <= 9 else new_deadline_hour}", reply_markup=None)
    await cq.message.answer(task.show_to_message(user_tz), reply_markup=for_task_info_kb(task), parse_mode='HTML')
    await state.clear()


@update_task_router.callback_query(F.data.startswith('mark_done_'))
async def mark_task_as_done(cq: types.CallbackQuery, state: FSMContext):
    await cq.answer()
    task_id = int(cq.data.split('_')[-1])
    client = BackendClient(cq.from_user.username)
    await client.finish_task(task_id)
    await cq.message.answer("Task done!", reply_markup=back_kb(task_id))
    await state.clear()
