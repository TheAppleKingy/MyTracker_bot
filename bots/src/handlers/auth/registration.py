from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext

from states.auth_states import RegistrationStates
from api.client import BackendClient
from keyboards.auth import check_active_kb, login_kb
from ..routers import auth_router


@auth_router.callback_query(F.data == 'reg_start')
async def ask_email(cq: types.CallbackQuery, state: FSMContext):
    await cq.answer()
    await cq.message.answer("Please send me your email")
    await state.set_state(RegistrationStates.waiting_email)


@auth_router.message(RegistrationStates.waiting_email)
async def ask_first_name(message: types.Message, state: FSMContext):
    await state.update_data(email=message.text)
    await message.answer("Please send me your name")
    await state.set_state(RegistrationStates.waiting_first_name)
    await message.delete()


@auth_router.message(RegistrationStates.waiting_first_name)
async def ask_last_name(message: types.Message, state: FSMContext):
    await state.update_data(first_name=message.text)
    await message.answer("Please send me your last name")
    await state.set_state(RegistrationStates.waiting_last_name)


@auth_router.message(RegistrationStates.waiting_last_name)
async def ask_password(message: types.Message, state: FSMContext):
    await state.update_data(last_name=message.text)
    await message.answer("Please send me password you'll use for authenticate in app")
    await state.set_state(RegistrationStates.waiting_password)


@auth_router.message(RegistrationStates.waiting_password)
async def register_user(message: types.Message, state: FSMContext):
    client = BackendClient()
    await state.update_data({'tg_name': message.from_user.username, 'password': message.text})
    data = await state.get_data()
    await client.register(**data)
    await message.answer("Now you have to confirm registration. Follow the link we sent to your email", reply_markup=check_active_kb())
    await message.delete()
    await state.clear()


@auth_router.callback_query(F.data == 'reg_confirmed')
async def confirm_registration(cq: types.CallbackQuery, state: FSMContext):
    await cq.answer()
    client = BackendClient(for_tg_name=cq.from_user.username)
    resp = await client.check_is_active()
    if resp.status == 200:
        await cq.message.edit_reply_markup(reply_markup=None)
        return await cq.message.answer("Registration confirmed!", reply_markup=login_kb())
    await cq.message.answer("You did not follow the link. Confirm registration by following the link in mail and try again")
