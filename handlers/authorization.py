from aiogram import Router, Bot
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters import Command, Text

from db.models import Coaches, Students

from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from keyboards.for_auth import auth, telephone, status, confirm, coach_list
from handlers.start_bot import make_start_message


auth_router = Router()


class Auth(StatesGroup):
    auth_state = State()
    choosing_coach = State()


@auth_router.message(Command("join"))
async def start_auth(message: Message, bot: Bot, state: FSMContext):
    await state.set_state(Auth.auth_state)
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    id_tg = message.from_user.id
    coach = await Coaches.get(tg_id=id_tg)
    student = await Students.get(tg_id=id_tg)
    if coach or student:
        await bot.send_message(
            chat_id=message.chat.id,
            text="Вы уже зарегистрированы!",
            disable_notification=False
        )
        await state.clear()
    else:
        await message.answer("<b>Вы хотите зарегистрироваться?</b>", parse_mode="HTML", reply_markup=auth())


@auth_router.callback_query(Text(text="auth"))
async def join(callback: CallbackQuery,state: FSMContext, bot: Bot):
    await state.update_data(tg_id=callback.from_user.id)
    await state.update_data(first_name=callback.from_user.first_name)

    if callback.from_user.username:
        await state.update_data(username=callback.from_user.username)
    else:
        await state.update_data(username="")
    await callback.message.delete()
    await callback.message.answer("<b>Отправьте нам свой номер телефона для обратной связи</b>", parse_mode="HTML", reply_markup=telephone())
    await callback.answer()


@auth_router.message(Text, Auth.auth_state)
async def save_contact(message: Message, state: FSMContext, bot: Bot):
    flag = False
    if message.contact:
        await message.answer(text="<b>Номер сохранён!</b>", parse_mode="HTML", reply_markup=ReplyKeyboardRemove())
        phone_number = message.contact.phone_number
        flag = True
    elif message.text == "Пропустить":
        phone_number = "Неизвестный"
        flag = True
    if flag:
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
        await message.delete()
        await state.update_data(telephone=phone_number)
        await message.answer("<b>Выберите ваш статус:</b>", parse_mode="HTML", reply_markup=status())
    else:
        await message.answer("<b>Выберите действие!</b>", parse_mode="HTML", reply_markup=telephone())



@auth_router.callback_query(Text(startswith="status"), Auth.auth_state)
async def confirm_auth(callback: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    phone: str = data["telephone"]
    if phone.isdigit():
        await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id - 1)
    status = callback.data.split(".")[1]
    print(status)
    if status == "coach":
        await state.update_data(is_coach=True)
    elif status == "student":
        await state.update_data(is_coach=False)

    if status in ["coach", "student"]:
        user = await state.get_data()
        if user['is_coach']:
            status = "Тренер"
        else:
            status = "Ученик"
        await callback.message.edit_text(
            f"<b>Проверьте данные:</b>\n<i>Номер телефона: {user['telephone']}\nСтатус: {status}</i>",
            parse_mode="HTML",
            reply_markup=confirm()
        )
        await callback.answer()
    else:
        await callback.answer(text="Выберите ваш статус!", show_alert=True)


@auth_router.callback_query(Text(text="good"), Auth.auth_state)
async def save_user(callback: CallbackQuery, state: FSMContext, bot: Bot):
    user = await state.get_data()
    print(user)
    if user['is_coach']:
        await Coaches.create(
            tg_id=int(user['tg_id']),
            first_name=user['first_name'],
            username=user['username'],
            telephone=user['telephone'],
        )
    else:
        await Students.create(
            tg_id=int(user['tg_id']),
            first_name=user['first_name'],
            username=user['username'],
            telephone=user['telephone'],
        )
    await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
    await state.clear()
    await callback.answer(text="Вы успешно зарегистрировались!", show_alert=True)


@auth_router.callback_query(Text(text="AuthCancel"), Auth.auth_state)
async def cancel(callback: CallbackQuery, bot: Bot, state: FSMContext):
    await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
    await state.clear()
    await callback.answer(text="Ошибка авторизации", show_alert=True)
    await callback.message.answer(make_start_message(callback), parse_mode="HTML")


@auth_router.message(Command("choose_coach"))
async def choose_coach(message: Message, bot: Bot, state: FSMContext):
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    await state.set_state(Auth.choosing_coach)
    keyboard = await coach_list()
    id_tg = message.from_user.id
    student = await Students.get(tg_id=id_tg)
    coach = await Coaches.get(tg_id=id_tg)
    if student:
        if student.coach_id:
            await message.answer("<b>У вас есть тренер!</b>", parse_mode="HTML")
        else:
            await message.answer(text="<b>Выберите тренера:</b>", parse_mode="HTML", reply_markup=keyboard)
    elif coach:
        await message.answer("<b>Вы являетесь тренером!</b>", parse_mode="HTML")
    else:
        await message.answer("<b>Вы не зарегистрированы!</b>", parse_mode="HTML")


@auth_router.callback_query(Auth.choosing_coach)
async def save_coach(callback: CallbackQuery, bot: Bot, state: FSMContext):
    await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
    coach_id = int(callback.data)
    id_tg = callback.from_user.id
    coach = await Coaches.get(id=coach_id)
    student = await Students.get(tg_id=id_tg)
    await student.update(coach_id=coach.id)
    await callback.answer(text=f"Ваш новый тренер: {coach.first_name}!", show_alert=True)
    await state.clear()

