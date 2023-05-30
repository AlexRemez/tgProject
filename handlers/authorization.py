from aiogram import Router, Bot, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters import Command, Text

from db.models import Coaches, Students, Athletes

from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from keyboards.for_auth import auth, telephone, status, confirm, coach_list, save_athlete_kb, athlete_notify
from handlers.start_bot import make_start_message
from keyboards.for_exam import start_exam
from keyboards.for_menu import main_menu_kb
from keyboards.for_start_bot import main_buttons_kb, back_menu_kb

import re

auth_router = Router()


class Auth(StatesGroup):
    auth_state = State()
    choosing_coach = State()
    change_coach = State()
    athlete_first_name = State()
    athlete_last_name = State()
    athlete_email = State()
    delete_athlete = State()


@auth_router.callback_query(Text(text="auth"))
async def join(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await state.set_state(Auth.auth_state)
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
    elif message.text.startswith("Пропустить"):
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
    await state.clear()
    await callback.answer(text="Вы успешно зарегистрировались!", show_alert=True)
    await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
    await callback.message.answer(make_start_message(callback), parse_mode="HTML", reply_markup=main_buttons_kb())


@auth_router.callback_query(Text(text="AuthCancel"), Auth.auth_state)
async def cancel(callback: CallbackQuery, bot: Bot, state: FSMContext):
    await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
    await state.clear()
    await callback.answer(text="Ошибка авторизации", show_alert=True)
    await callback.message.answer(make_start_message(callback), parse_mode="HTML", reply_markup=main_buttons_kb())


@auth_router.message(Command("choose_coach"))
async def choose_coach(message: Message, bot: Bot, state: FSMContext):
    await message.delete()
    await state.set_state(Auth.choosing_coach)
    keyboard = await coach_list()
    id_tg = message.from_user.id
    student = await Students.get(tg_id=id_tg)
    coach = await Coaches.get(tg_id=id_tg)
    if student:
        if student.coach_id:
            await message.answer("<b>У вас есть тренер!</b>", parse_mode="HTML")
            await state.clear()
        else:
            await message.answer(text="<b>Выберите тренера:</b>", parse_mode="HTML", reply_markup=keyboard)
    elif coach:
        await message.answer("<b>Вы являетесь тренером!</b>", parse_mode="HTML")
        await state.clear()
    else:
        await message.answer("<b>Вы не зарегистрированы!</b>", parse_mode="HTML")
        await state.clear()


@auth_router.callback_query(Text(text="choose_coach"))
async def choose_coach(callback: CallbackQuery, state: FSMContext):
    # await callback.message.delete()
    await state.set_state(Auth.choosing_coach)
    id_tg = callback.from_user.id
    student = await Students.get(tg_id=id_tg)
    coach = await Coaches.get(tg_id=id_tg)
    if student:
        if student.coach_id:
            await callback.answer("У вас есть тренер!")
            await state.clear()
        else:
            keyboard = await coach_list()
            await callback.message.edit_text(text="<b>Выберите тренера:</b>",
                                             parse_mode="HTML",
                                             reply_markup=keyboard)
            await callback.answer()
    elif coach:
        await callback.answer("Вы являетесь тренером!")
        await state.clear()
    else:
        await callback.answer("Вы не зарегистрированы!")
        await state.clear()


@auth_router.callback_query(Text(text="delete_coach"))
async def delete_coach(callback: CallbackQuery, state: FSMContext):
    id_tg = callback.from_user.id
    student = await Students.get(tg_id=id_tg)
    await student.update(coach_id=None)
    await callback.answer(text="Тренер удалён!", show_alert=True)


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


################################################################
# Регистрация спортсмена для экзамена

@auth_router.message(Auth.athlete_first_name, Text)
async def first_name_handler(message: Message, state: FSMContext):
    first_name = message.text.capitalize()
    if first_name.isalpha():
        await state.update_data(athlete_first_name=first_name)
        await state.set_state(Auth.athlete_last_name)
        await message.answer(
            text="<b>Введите свою фамилию</b>"
                 "\n\n<u>Пожалуйста вводите действительную информацию, ваши данные будут проверены!</u>",
            reply_markup=back_menu_kb(text="Отмена")
        )


@auth_router.message(Auth.athlete_last_name, Text)
async def last_name_handler(message: Message, state: FSMContext):
    last_name = message.text.capitalize()
    if last_name.isalpha():
        await state.update_data(athlete_last_name=last_name)
        await state.set_state(Auth.athlete_email)
        await message.answer(
            text="<b>Введите свою почту</b>"
                 "\n<i>example@gmail.com</i>"
                 "\n\n<u>Пожалуйста вводите действительную информацию, ваши данные будут проверены!</u>",
            reply_markup=back_menu_kb(text="Отмена")
        )


@auth_router.message(Auth.athlete_email, Text)
async def check_handler(message: Message, state: FSMContext):
    email = message.text
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    match = re.match(pattern, email)
    if match is not None:
        await state.update_data(athlete_email=email)

        data = await state.get_data()
        first_name = data['athlete_first_name']
        last_name = data['athlete_last_name']
        email = data['athlete_email']

        await message.answer(
            text="<b>Проверьте данные</b>"
                 f"\n\n<b>Имя:</b> {first_name}"
                 f"\n<b>Фамилия:</b> {last_name}"
                 f"\n<b>Почта:</b> {email}",
            reply_markup=save_athlete_kb()
        )


@auth_router.callback_query(Auth.athlete_email, Text(text="save_athlete"))
async def save_athlete(callback: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    first_name = data['athlete_first_name']
    last_name = data['athlete_last_name']
    email = data['athlete_email']
    tg_id = callback.from_user.id

    await Athletes.create(
        tg_id=tg_id,
        first_name=first_name,
        last_name=last_name,
        email=email
    )

    await callback.answer("Заявка подана☑️ Ожидайте подтверждения⏳", show_alert=True)
    await callback.message.edit_text(text="<b>⏳Ожидайте пока вашу заявку одобрят⏳</b>"
                                          "\n<i>Вы можете пользоваться ботом во время ожидания🤖</i>")
    await state.clear()
    await bot.send_message(
        chat_id=5691938305,
        text="💬<b>Заявка на лидерборд</b>💬"
             f"\n\n<b>Имя:</b> {first_name}"
             f"\n<b>Фамилия:</b> {last_name}"
             f"\n<b>Почта:</b> {email}",
        reply_markup=athlete_notify(tg_id)
    )


@auth_router.callback_query(Text(startswith="athlete_active-"))
async def athlete_active(callback: CallbackQuery, bot: Bot):
    tg_id = callback.data.split("-")[1]
    athlete = await Athletes.get(tg_id=int(tg_id))
    await athlete.update(is_active=True)
    await callback.message.delete()
    await callback.answer(text="Данные спортмена сохранены✅")
    await bot.send_message(chat_id=tg_id, text="<b>✅Ваша заявка одобрена✅</b>", reply_markup=start_exam())


@auth_router.callback_query(Text(startswith="delete_athlete"))
async def delete_athlete(callback: CallbackQuery, state: FSMContext):
    tg_id = callback.data.split("-")[1]
    await state.update_data(athlete_tg_id=int(tg_id))
    athlete = await Athletes.get(tg_id=int(tg_id))
    await athlete.delete()
    await callback.message.edit_text(text="Опишите причину отказа📝")
    await state.set_state(Auth.delete_athlete)


@auth_router.message(Auth.delete_athlete, Text)
async def rejection_reason_handler(message: Message, state: FSMContext, bot: Bot):
    rejection_reason = message.text
    text = f"<b>❌Заявка отклонена❌</b>" \
           f"\n\n<i>{rejection_reason}</i>"
    data = await state.get_data()
    tg_id = data['athlete_tg_id']
    await bot.send_message(chat_id=tg_id, text=text)