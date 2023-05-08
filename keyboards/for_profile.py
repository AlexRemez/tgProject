from _ast import In

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from db.models import Coaches, Students


def coach_services() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.row(
        InlineKeyboardButton(text="👥Мои ученики👥", callback_data="my_students"),
        InlineKeyboardButton(text="🆕Добавить упражнение🆕", callback_data="add_exercise")
    )
    kb.row(InlineKeyboardButton(text="🗒Список задач🗒", callback_data="coach_tasks"))
    kb.row(InlineKeyboardButton(text="❌Удалить аккаунт❌", callback_data="confirm_delete"))
    return kb.as_markup(resize_keyboard=True)


def student_services(coach) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    if coach:
        my_coach_button = InlineKeyboardButton(text="👤Мой тренер👤", callback_data="my_coach")
    else:
        my_coach_button = InlineKeyboardButton(text="🟡Выбрать тренера", callback_data="choose_coach")
    kb.row(
        my_coach_button,
        InlineKeyboardButton(text="🗒Список задач🗒", callback_data="student_tasks")
    )
    kb.row(InlineKeyboardButton(text="❌Удалить аккаунт❌", callback_data="confirm_delete"))
    return kb.as_markup(resize_keyboard=True)


async def student_list_kb(coach: Coaches, previous_step) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    students = await Students.filter(coach_id=coach.id)
    if previous_step == "coach_process_tasks":
        spliter = "&"
    elif previous_step == "coach_tasks":
        spliter = "*"
    else:
        spliter = "#"
    for student in students:
        student: Students
        kb.add(InlineKeyboardButton(text=f"{student.first_name}", callback_data=spliter + str(student.id)))
    kb.adjust(4)
    kb.row(InlineKeyboardButton(text="Назад", callback_data=previous_step))
    return kb.as_markup(resize_keyboard=True)


def coach_tasks_list_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text="Выполненные задачи", callback_data="coach_completed_tasks"))
    kb.row(InlineKeyboardButton(text="В процессе", callback_data="coach_process_tasks"),
           InlineKeyboardButton(text="Ожидают подтверждения", callback_data="coach_waiting_confirm"))
    kb.row(InlineKeyboardButton(text="Назад", callback_data="profile"))
    return kb.as_markup(resize_keyboard=True)


def student_tasks_list_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.row(
        InlineKeyboardButton(text="Выполненные задачи", callback_data="student_completed_tasks"),
        InlineKeyboardButton(text="В процессе", callback_data="student_process_tasks"))
    kb.row(InlineKeyboardButton(text="Назад", callback_data="profile"))
    return kb.as_markup(resize_keyboard=True)


def add_task() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text="🆕Добавить задачу🆕", callback_data="add_task"))
    kb.row(InlineKeyboardButton(text="Назад", callback_data="coach_tasks"))
    return kb.as_markup(resize_keyboard=True)


def confirm_kb(previous_step) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text="Подтвердить", callback_data="confirm"))
    kb.row(InlineKeyboardButton(text="Назад", callback_data=previous_step))
    return kb.as_markup(resize_keyboard=True)


def student_confirm_kb(previous_step) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text="Подтвердить", callback_data="student_confirm"))
    kb.row(InlineKeyboardButton(text="Назад", callback_data=previous_step))
    return kb.as_markup(resize_keyboard=True)


def back(previous_step) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text="Назад", callback_data=previous_step))
    return kb.as_markup(resize_keyboard=True)


def my_coach_kb(previous_step) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text="❌Убрать тренера❌", callback_data="delete_coach"),
           InlineKeyboardButton(text="↩️Назад↩️", callback_data=previous_step))
    return kb.as_markup(resize_keyboard=True)


def delete_account_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text="❌Удалить❌", callback_data="delete_account"))
    kb.row(InlineKeyboardButton(text="Отмена", callback_data="del_cancel"))
    return kb.as_markup(resize_keyboard=True)