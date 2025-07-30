from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext

from states.auth_states import RegistrationStates
from api.client import BackendClient
from keyboards.auth import check_active_kb, login_kb
from keyboards.settings import settings_kb


registration_router = Router(name="Registration")


@registration_router.callback_query(F.data == 'reg_start')
async def ask_email(cq: types.CallbackQuery, state: FSMContext):
    await cq.answer()
    await cq.message.answer("Please send me your email")
    await state.set_state(RegistrationStates.waiting_email)


@registration_router.message(RegistrationStates.waiting_email)
async def ask_first_name(message: types.Message, state: FSMContext):
    await state.update_data(email=message.text)
    await message.answer("Please send me your name")
    await state.set_state(RegistrationStates.waiting_first_name)
    await message.delete()


@registration_router.message(RegistrationStates.waiting_first_name)
async def ask_last_name(message: types.Message, state: FSMContext):
    await state.update_data(first_name=message.text)
    await message.answer("Please send me your last name")
    await state.set_state(RegistrationStates.waiting_last_name)


@registration_router.message(RegistrationStates.waiting_last_name)
async def ask_password(message: types.Message, state: FSMContext):
    await state.update_data(last_name=message.text)
    await message.answer("Please send me password you'll use for authenticate in app")
    await state.set_state(RegistrationStates.waiting_password)


@registration_router.message(RegistrationStates.waiting_password)
async def ask_city(message: types.Message, state: FSMContext):
    await state.update_data(password=message.text)
    await state.update_data({'tg_name': message.from_user.username})
    await message.delete()
    data = await state.get_data()
    await state.clear()
    client = BackendClient(message.from_user.username)
    await client.register(**data)
    await message.answer("Now you have to confirm registration. Follow the link we sent to your email", reply_markup=check_active_kb())


@registration_router.callback_query(F.data == 'reg_confirmed')
async def confirm_registration(cq: types.CallbackQuery, state: FSMContext):
    await cq.answer()
    client = BackendClient(for_tg_name=cq.from_user.username)
    await client.check_is_active()
    await cq.message.answer("Now you have to go to settings and define your timezone", reply_markup=settings_kb())
    await cq.message.edit_text(text='Registration confirmed!', reply_markup=login_kb())
