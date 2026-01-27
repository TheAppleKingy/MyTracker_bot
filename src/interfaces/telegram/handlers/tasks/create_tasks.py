from datetime import datetime, timezone

from aiogram import types, F, Router
from aiogram.fsm.context import FSMContext
from aiogram3_calendar import simple_cal_callback, SimpleCalendar as calendar
from dishka.integrations.aiogram import FromDishka

from src.interfaces.telegram.keyboards.tasks import for_task_info_kb, kalendar_kb, deadline_time_kb
from src.interfaces.telegram.states.task_states import CreateTaskStates
from src.interfaces.presentators.task import show_task_data
from src.application.interfaces.tz_gateway import TimezoneGatewayInterface
from src.application.interfaces.api_client import BackendClientInterface


create_task_router = Router(name='Create tasks')


@create_task_router.callback_query(F.data == 'create_task')
async def ask_title(cq: types.CallbackQuery, state: FSMContext):
    await cq.answer()
    await state.clear()
    await state.set_state(CreateTaskStates.waiting_title)
    return await cq.message.answer("Send me task title")


@create_task_router.message(CreateTaskStates.waiting_title)
async def ask_description(message: types.Message, state: FSMContext):
    await state.update_data({'title': message.text})
    await state.set_state(CreateTaskStates.waiting_description)
    return await message.answer('Send me description of task')


@create_task_router.message(CreateTaskStates.waiting_description)
async def check_tz(message: types.Message, state: FSMContext, tz_gateway: FromDishka[TimezoneGatewayInterface]):
    await state.update_data({'description': message.text})
    await state.set_state(CreateTaskStates.waiting_deadline)
    user_tz = await tz_gateway.get_tz(message.from_user.username)
    if not user_tz:
        pass
    now_local = datetime.now(timezone.utc).astimezone(user_tz)
    return await message.answer(
        'Choose deadline date',
        reply_markup=await kalendar_kb(now_local.year, now_local.month)
    )


@create_task_router.callback_query(simple_cal_callback.filter(), CreateTaskStates.waiting_deadline)
async def ask_deadline_date(
    cq: types.CallbackQuery,
    callback_data: simple_cal_callback,
    state: FSMContext,
    tz_gateway: FromDishka[TimezoneGatewayInterface]
):
    await cq.answer()
    selected, date = await calendar().process_selection(cq, callback_data)
    if not selected:
        return
    user_tz = await tz_gateway.get_tz(cq.from_user.username)
    if not user_tz:
        pass
    selected_local: datetime = date.replace(tzinfo=user_tz)
    await state.update_data(deadline=date.isoformat())
    await cq.message.edit_text(f"Choosen deadline date is {selected_local.strftime('%Y-%m-%d')}", reply_markup=None)
    return await cq.message.answer("Select deadline time", reply_markup=deadline_time_kb(user_tz, date))


@create_task_router.callback_query(F.data.startswith('set_deadline_hour_'))
async def set_deadline_time(
    cq: types.CallbackQuery,
    state: FSMContext,
    tz_gateway: FromDishka[TimezoneGatewayInterface],
    backend: FromDishka[BackendClientInterface]
):
    await cq.message.edit_reply_markup(reply_markup=None)
    deadline_hour = int(cq.data.split('_')[-1])
    data = await state.get_data()
    await state.clear()
    user_tz = await tz_gateway.get_tz(cq.from_user.username)
    if not user_tz:
        pass
    deadline_utc = datetime.fromisoformat(data.get('deadline')).replace(
        hour=deadline_hour, tzinfo=user_tz)
    data.update({'deadline': deadline_utc.isoformat()})
    data.pop('rollback_msg', None)
    created = await backend.create_task(**data)
    await cq.message.edit_text(f"Choosen deadline time is {'0'+deadline_hour if deadline_hour <= 9 else deadline_hour}h:00m")
    await cq.message.answer(show_task_data(created, user_tz), reply_markup=for_task_info_kb(created), parse_mode='HTML')


@create_task_router.callback_query(F.data.startswith('create_subtask_'))
async def create_subtask(cq: types.CallbackQuery, state: FSMContext):
    await cq.answer()
    await state.clear()
    parent_id = int(cq.data.split('_')[-1])
    await state.update_data(task_id=parent_id)
    await state.set_state(CreateTaskStates.waiting_title)
    return await cq.message.answer('Send me subtask title')
