from aiogram import Router, Bot, F
from aiogram.filters import Command, Text
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from db.models import Students, Coaches
from handlers.authorization import Auth

from keyboards.for_auth import auth
from keyboards.for_menu import main_menu_kb
from keyboards.for_profile import coach_services, student_services

menu_router = Router()


@menu_router.message(Text(text="⭐️Меню"))
async def main_menu(message: Message):
    id_tg = message.from_user.id
    coach = await Coaches.get(tg_id=id_tg)
    student = await Students.get(tg_id=id_tg)
    if coach or student:
        await message.answer("⭐️ <b>Меню</b> ⭐️", reply_markup=main_menu_kb(auth=True))
    else:
        await message.answer("⭐️ <b>Меню</b> ⭐️", reply_markup=main_menu_kb(auth=False))


@menu_router.callback_query(Text(text="main_menu"))
async def main_menu(callback: CallbackQuery):
    id_tg = callback.from_user.id
    coach = await Coaches.get(tg_id=id_tg)
    student = await Students.get(tg_id=id_tg)
    if coach or student:
        await callback.message.edit_text("⭐️ <b>Меню</b> ⭐️", reply_markup=main_menu_kb(auth=True))
    else:
        await callback.message.edit_text("⭐️ <b>Меню</b> ⭐️", reply_markup=main_menu_kb(auth=False))


@menu_router.callback_query(Text(text="hide_menu"))
async def hide_menu(callback: CallbackQuery):
    await callback.message.delete()
    await callback.answer(text="Вы скрыли меню")


@menu_router.message(Command("profile"))
async def check_profile(message: Message, state: FSMContext):
    await message.delete()
    student = await Students.get(tg_id=message.from_user.id)
    coach = await Coaches.get(tg_id=message.from_user.id)
    await state.update_data(previous_messages=[])
    if coach:
        students_list = await Students.filter(coach_id=coach.id)
        await message.answer(
            f"\
            👤<b>Ваш профиль тренера</b>👤\
            \n⚫️Никнейм: {coach.first_name}\
            \n📱Номер телефона: {coach.telephone}\
            \n👥Количество учеников: {len(students_list)}\
            \n📅Дата регистрации профиля: {coach.date_auth}\
            ",
            parse_mode="HTML",
            reply_markup=coach_services()
        )
    elif student:
        coach = await Coaches.get(id=student.coach_id)
        if coach:
            coach_name = coach.first_name
        else:
            coach_name = "Нет тренера"
        await message.answer(
            f"\
            👤<b>Ваш профиль</b>👤\
            \n⚪️Никнейм: {student.first_name}\
            \n📱Номер телефона: {student.telephone}\
            \n⚫️Ваш тренер: {coach_name}\
            \n📅Дата регистрации профиля: {student.date_auth}\
            ",
            parse_mode="HTML",
            reply_markup=student_services(coach)
        )
    else:
        await message.answer("<b>Вы не зарегистрированы!</b>", parse_mode="HTML", reply_markup=None)


@menu_router.callback_query(Text(text="profile"))
async def check_profile(callback: CallbackQuery, state: FSMContext):
    student = await Students.get(tg_id=callback.from_user.id)
    coach = await Coaches.get(tg_id=callback.from_user.id)
    await state.update_data(previous_messages=[])
    if coach:
        students_list = await Students.filter(coach_id=coach.id)
        await callback.message.edit_text(
            f"\
            👤<b>Ваш профиль тренера</b>👤\
            \n⚫️Никнейм: {coach.first_name}\
            \n📱Номер телефона: {coach.telephone}\
            \n👥Количество учеников: {len(students_list)}\
            \n📅Дата регистрации профиля: {coach.date_auth}\
            ",
            parse_mode="HTML",
            reply_markup=coach_services()
        )
    elif student:
        coach = await Coaches.get(id=student.coach_id)
        if coach:
            coach_name = coach.first_name
        else:
            coach_name = "Нет тренера"
        await callback.message.edit_text(
            f"\
            👤<b>Ваш профиль</b>👤\
            \n⚪️Никнейм: {student.first_name}\
            \n📱Номер телефона: {student.telephone}\
            \n⚫️Ваш тренер: {coach_name}\
            \n📅Дата регистрации профиля: {student.date_auth}\
            ",
            parse_mode="HTML",
            reply_markup=student_services(coach)
        )
    else:
        await callback.message.answer("<b>Вы не зарегистрированы!</b>", parse_mode="HTML", reply_markup=None)


@menu_router.message(Command("join"))
async def start_auth(message: Message, bot: Bot, state: FSMContext):
    await state.set_state(Auth.auth_state)
    await message.delete()
    id_tg = message.from_user.id
    coach = await Coaches.get(tg_id=id_tg)
    student = await Students.get(tg_id=id_tg)
    if coach or student:
        await message.answer("<b>Вы уже зарегистрированы!</b>", parse_mode="HTML")
        await state.clear()
    else:
        await message.answer("<b>Вы хотите зарегистрироваться?</b>", parse_mode="HTML", reply_markup=auth())


@menu_router.callback_query(Text(text="join"))
async def start_auth(callback: CallbackQuery, bot: Bot, state: FSMContext):
    await state.set_state(Auth.auth_state)
    await callback.message.delete()
    id_tg = callback.from_user.id
    coach = await Coaches.get(tg_id=id_tg)
    student = await Students.get(tg_id=id_tg)
    if coach or student:
        await callback.answer("<b>Вы уже зарегистрированы!</b>", parse_mode="HTML", show_alert=True)
        await state.clear()
    else:
        await callback.message.answer("<b>Вы хотите зарегистрироваться?</b>", parse_mode="HTML", reply_markup=auth())
