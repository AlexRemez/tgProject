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


def waiting_confirm_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text="Подробнее", callback_data="more"))
    kb.row(InlineKeyboardButton(text="Назад", callback_data="back"))
    return kb.as_markup(resize_keyboard=True)


def back() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text="Назад", callback_data="back"))
    return kb.as_markup(resize_keyboard=True)