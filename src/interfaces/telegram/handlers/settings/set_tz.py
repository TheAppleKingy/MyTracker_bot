from aiogram import types, F, Router
from aiogram.fsm.context import FSMContext
from dishka.integrations.aiogram import FromDishka

from src.application.interfaces.clients import CountryClientInterface, TimezoneClientInterface
from src.application.interfaces import StorageInterface
from src.interfaces.telegram.states.settings import SetTZStates
from src.interfaces.telegram.keyboards.settings import timezones_page_kb
from src.interfaces.telegram.keyboards.shared import main_page_kb, back_kb
from src.logger import logger

tz_router = Router(name="Set timezone")


@tz_router.callback_query(F.data.startswith('set_timezone'))
async def set_timezone(
    cq: types.CallbackQuery,
    state: FSMContext
):
    await cq.answer()
    await state.clear()
    await cq.message.answer("Send me your country name")
    await state.set_state(SetTZStates.waiting_country)


@tz_router.message(SetTZStates.waiting_country)
async def search_tzinfo_by_country(
    message: types.Message,
    state: FSMContext,
    country_client: FromDishka[CountryClientInterface],
    tz_client: FromDishka[TimezoneClientInterface],
):
    country_code = country_client.get_country_code_by_name(message.text)
    if not country_code:
        return await message.answer(text="Enter valid country name", reply_markup=None)
    offsets = await tz_client.get_country_tz_offsets_minutes(country_code)
    if not offsets:
        await state.clear()
        return await message.answer(
            text="Timezones not found. Try again or write to support",
            reply_markup=back_kb("settings")
        )
    await state.update_data(offsets=offsets)
    await message.answer("Select your timezone", reply_markup=timezones_page_kb(1, 5, offsets))


@tz_router.callback_query(F.data.startswith("timezones_page_"))
async def another_tz_page(
    cq: types.CallbackQuery,
    state: FSMContext,
):
    await cq.answer()
    page = int(cq.data.split("_")[-1])
    await cq.message.edit_reply_markup(reply_markup=timezones_page_kb(page, 5, await state.get_value("offsets")))


@tz_router.callback_query(F.data.startswith("set_tz_offset_"))
async def set_user_tz(
    cq: types.CallbackQuery,
    state: FSMContext,
    storage: FromDishka[StorageInterface]
):
    await cq.answer()
    prepared_callback_data = cq.data.split("_")
    choosen_offset = int(prepared_callback_data[-1])
    presented = prepared_callback_data[-2]
    await storage.set_tz(cq.from_user.username, choosen_offset)
    await state.clear()
    return await cq.message.edit_text(
        text=f"Choosen timezone {presented}",
        reply_markup=back_kb("settings")
    )
