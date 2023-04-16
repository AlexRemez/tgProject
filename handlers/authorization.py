from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, Contact, ReplyKeyboardRemove

from db.models import User
from aiogram import Router, F, Bot
from aiogram.filters import Command, Text
from aiogram.fsm.context import FSMContext
from sqlalchemy import select, func, insert
from db.connect import async_db_session
from handlers.start_bot import make_start_message
from keyboards.for_auth import auth, telephone, status, confirm


auth_router = Router()


class Auth(StatesGroup):
    auth_state = State()


@auth_router.message(Command("join"))
async def start_auth(message: Message, bot: Bot):
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    id_tg = message.from_user.id
    async with async_db_session() as session:
        users = await session.execute(select(User).where(User.tg_id == id_tg))
        user = users.fetchone()
        print(user)
        if user:
            await bot.send_message(
                chat_id=message.chat.id,
                text="Вы уже зарегистрированы!",
                disable_notification=False
            )
        else:
            await message.answer("<b>Вы хотите зарегистрироваться?</b>", parse_mode="HTML", reply_markup=auth())


@auth_router.callback_query(Text(text="auth"))
async def join(callback: CallbackQuery,state: FSMContext, bot: Bot):
    await state.set_state(Auth.auth_state)
    await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
    await state.update_data(tg_id=callback.from_user.id)
    await state.update_data(first_name=callback.from_user.first_name)

    if callback.from_user.username:
        await state.update_data(username=callback.from_user.username)
    else:
        await state.update_data(username="")
    await callback.message.answer("<b>Отправьте нам свой номер телефона для обратной связи</b>",
                                  parse_mode="HTML",
                                  reply_markup=telephone())
    await callback.answer()


@auth_router.message(Text, Auth.auth_state)
async def save_contact(message: Message, state: FSMContext, bot: Bot):
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    if message.contact:
        await message.answer(text="<b>Номер сохранён!</b>", parse_mode="HTML", reply_markup=ReplyKeyboardRemove())
        phone_number = message.contact.phone_number
        await state.update_data(telephone=phone_number)
        await message.answer("<b>Выберите ваш статус:</b>", parse_mode="HTML", reply_markup=status())
    else:
        await message.answer("<b>Нажмите на кнопку 'Отправить номер'!</b>", parse_mode="HTML", reply_markup=telephone())


@auth_router.callback_query(Text(startswith="status"), Auth.auth_state)
async def confirm_auth(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
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
        await callback.message.answer(
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
    async with async_db_session() as session:
        await session.execute(insert(User).values(
            tg_id=int(user['tg_id']),
            first_name=user['first_name'],
            username=user['username'],
            telephone=user['telephone'],
            is_coach=user['is_coach']
        ))
        await session.commit()
    await state.clear()
    await callback.answer(text="Вы успешно зарегистрировались!", show_alert=True)
    await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)



@auth_router.callback_query(Text(text="AuthCancel"), Auth.auth_state)
async def cancel(callback: CallbackQuery, bot: Bot, state: FSMContext):
    await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
    await state.clear()
    await callback.answer(text="Ошибка авторизации", show_alert=True)
    await callback.message.answer(make_start_message(callback), parse_mode="HTML")
