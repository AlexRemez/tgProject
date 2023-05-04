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
    kb.row(InlineKeyboardButton(text="🗒Список задач🗒", callback_data="tasks"))
    kb.row(InlineKeyboardButton(text="❌Удалить аккаунт❌", callback_data="confirm_delete"))
    return kb.as_markup(resize_keyboard=True)


def student_services() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.row(
        InlineKeyboardButton(text="👤Мой тренер👤", callback_data="my_coach"),
        InlineKeyboardButton(text="🗒Список задач🗒", callback_data="tasks")
    )
    kb.row(InlineKeyboardButton(text="❌Удалить аккаунт❌", callback_data="confirm_delete"))
    return kb.as_markup(resize_keyboard=True)


async def student_list_kb(coach: Coaches) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    students = await Students.filter(coach_id=coach.id)
    for student in students:
        student: Students
        kb.add(InlineKeyboardButton(text=f"{student.first_name}", callback_data="#" + str(student.id)))
    kb.adjust(4)
    kb.row(InlineKeyboardButton(text="Назад", callback_data="back"))
    return kb.as_markup(resize_keyboard=True)


def tasks_list_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text="Выполненные задачи", callback_data="completed_tasks"))
    kb.row(InlineKeyboardButton(text="В процессе", callback_data="process_tasks"),
           InlineKeyboardButton(text="Ожидают подтверждения", callback_data="waiting_confirm"))
    kb.row(InlineKeyboardButton(text="Назад", callback_data="back"))
    return kb.as_markup(resize_keyboard=True)


def student_tasks_list_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.row(
        InlineKeyboardButton(text="Выполненные задачи", callback_data="student_completed_tasks"),
        InlineKeyboardButton(text="В процессе", callback_data="student_process_tasks"))
    kb.row(InlineKeyboardButton(text="Назад", callback_data="back"))
    return kb.as_markup(resize_keyboard=True)


def add_task() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text="🆕Добавить задачу🆕", callback_data="add_task"))
    kb.row(InlineKeyboardButton(text="Назад", callback_data="back"))
    return kb.as_markup(resize_keyboard=True)


def confirm_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text="Подтвердить", callback_data="confirm"))
    kb.row(InlineKeyboardButton(text="Назад", callback_data="back"))
    return kb.as_markup(resize_keyboard=True)


def student_confirm_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text="Подтвердить", callback_data="student_confirm"))
    kb.row(InlineKeyboardButton(text="Назад", callback_data="back"))
    return kb.as_markup(resize_keyboard=True)


def back() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text="Назад", callback_data="back"))
    return kb.as_markup(resize_keyboard=True)


def delete_account_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text="❌Удалить❌", callback_data="delete_account"))
    kb.row(InlineKeyboardButton(text="Отмена", callback_data="del_cancel"))
    return kb.as_markup(resize_keyboard=True)