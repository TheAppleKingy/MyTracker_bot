from aiogram import types, F, Router
from aiogram.fsm.context import FSMContext
from dishka.integrations.aiogram import FromDishka

from src.application.interfaces.clients import CountryClientInterface, TimezoneClientInterface
from src.application.interfaces import AsyncStorageInterface
from src.interfaces.handlers.telegram.states.settings import SetTZStates
from src.interfaces.presentators.telegram.keyboards.settings import timezones_page_kb
from src.interfaces.presentators.telegram.keyboards.shared import back_kb
from src.interfaces.handlers.telegram.errors import HandlerError
from src.logger import logger

tz_router = Router(name="Set timezone")


@tz_router.callback_query(F.data.startswith('set_timezone'))
async def set_timezone(
    event: types.CallbackQuery,
    context: FSMContext
):
    await event.answer()
    await context.clear()
    await event.message.answer("Send me your country name")
    await context.set_state(SetTZStates.waiting_country)


@tz_router.message(SetTZStates.waiting_country)
async def search_tzinfo_by_country(
    event: types.Message,
    context: FSMContext,
    country_client: FromDishka[CountryClientInterface],
    tz_client: FromDishka[TimezoneClientInterface],
):
    country_code = country_client.get_country_code_by_name(event.text)
    if not country_code:
        raise HandlerError("Enter valid country name", clear_context=False)
    offsets = await tz_client.get_country_tz_offsets_minutes(country_code)
    if not offsets:
        raise HandlerError(
            "Timezones not found. Try again or write to support",
            kb=back_kb("settings")
        )
    await context.update_data(offsets=offsets)
    await event.answer(
        text="<b>Select your timezone</b>",
        reply_markup=timezones_page_kb(1, 5, offsets),
        parse_mode="HTML"
    )


@tz_router.callback_query(F.data.startswith("timezones_page_"))
async def another_tz_page(
    event: types.CallbackQuery,
    context: FSMContext,
):
    await event.answer()
    page = int(event.data.split("_")[-1])
    await event.message.edit_reply_markup(reply_markup=timezones_page_kb(page, 5, await context.get_value("offsets")))


@tz_router.callback_query(F.data.startswith("set_tz_offset_"))
async def set_user_tz(
    event: types.CallbackQuery,
    context: FSMContext,
    storage: FromDishka[AsyncStorageInterface]
):
    await event.answer()
    prepared_callback_data = event.data.split("_")
    choosen_offset = int(prepared_callback_data[-1])
    presented = prepared_callback_data[-2]
    await storage.set_tz(event.from_user.username, choosen_offset)
    await context.clear()
    return await event.message.edit_text(
        text=f"<b>Choosen timezone {presented}</b>",
        reply_markup=back_kb("settings"),
        parse_mode="HTML"
    )
