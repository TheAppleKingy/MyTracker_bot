from pycountry import countries

from aiogram import types, F, Router
from aiogram.fsm.context import FSMContext

from states.settings_states import SetTZStates

from api.tz_client import get_country_timezones
from api.exc import TimezoneAPIError, NotAuthenticatedError
from api.redis_client import set_user_tz, get_token

from keyboards.settings import get_timezones_page_kb
from keyboards.tasks import get_my_tasks_kb
from keyboards.auth import login_kb

tz_router = Router(name="Set timezone")


@tz_router.callback_query(F.data.startswith('set_timezone'))
async def set_timezone(cq: types.CallbackQuery, state: FSMContext):
    await cq.answer()
    await cq.message.answer("Send me your country name")
    await state.set_state(SetTZStates.waiting_country)


@tz_router.message(SetTZStates.waiting_country)
async def search_tzinfo_by_country(message: types.Message, state: FSMContext):
    try:
        country_list = countries.search_fuzzy(message.text)
    except LookupError:
        await message.answer("Please enter correct country name")
    if len(country_list) > 1:
        await message.answer("Please enter correct country name")
    country_code = country_list[0].alpha_2
    try:
        country_timezones = await get_country_timezones(country_code)
    except TimezoneAPIError as e:
        await message.answer('Cannot get info about your city, please send me your timezone in format +7 | -2 | 0 (from UTC)')
        await state.set_state(SetTZStates.waiting_offset)
        return
    await state.update_data(timezones=country_timezones)
    await message.answer("Select your timezone", reply_markup=get_timezones_page_kb(1, 5, country_timezones))


@tz_router.message(SetTZStates.waiting_offset)
async def set_tz_as_offset(message: types.Message, state: FSMContext):
    offset = int(message.text)
    await set_user_tz(offset, message.from_user.username)
    kb = get_my_tasks_kb()
    try:
        await get_token(message.from_user.username)
    except NotAuthenticatedError:
        kb = login_kb()
    await message.answer("Timezone set", reply_markup=kb)
    await state.clear()


@tz_router.callback_query(F.data.startswith('timezones_page_'))
async def process_timezones(cq: types.CallbackQuery, state: FSMContext):
    await cq.answer()
    data = await state.get_data()
    page = int(cq.data.split('_')[-1])
    timezones = data.get('timezones')
    await cq.message.edit_reply_markup(reply_markup=get_timezones_page_kb(page, 5, timezones))


@tz_router.callback_query(F.data.startswith('tz='))
async def set_timezone(cq: types.CallbackQuery, state: FSMContext):
    await cq.answer()
    await cq.message.edit_reply_markup(reply_markup=None)
    tzinfo = cq.data.split('=')[-1]
    await set_user_tz(tzinfo, cq.from_user.username)
    await cq.message.answer("Timezone set", reply_markup=get_my_tasks_kb())
    await state.clear()
