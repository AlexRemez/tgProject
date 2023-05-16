from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from db.models import Exercises, Tasks, Students
from sqlalchemy import select
from db.connect import async_db_session


async def list_ex_kb() -> InlineKeyboardMarkup:
    ex_num_list = await Exercises.all()
    kb = InlineKeyboardBuilder()
    for ex_num in ex_num_list:
        ex_num = str(ex_num.id)
        kb.add(InlineKeyboardButton(text="№" + str(ex_num), callback_data="№" + str(ex_num)))
    kb.adjust(4)
    return kb.as_markup(resize_keyboard=True)


async def list_ex_tasks(tasks: Tasks, previous_step) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    num = 0
    for task in tasks:
        num += 1
        task: Tasks
        kb.add(InlineKeyboardButton(text="№" + str(task.exercise_id), callback_data="№" + str(task.id)))
    kb.adjust(5)
    kb.row(InlineKeyboardButton(text="↩️Назад", callback_data=previous_step))
    return kb.as_markup(resize_keyboard=True)


async def student_confirm_task_kb(student: Students) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    tasks = await Tasks.filter(student_id=student.id, coach_status=False, student_status=False)
    num = 0
    for task in tasks:
        num += 1
        task: Tasks
        kb.add(InlineKeyboardButton(text="№" + str(task.exercise_id), callback_data="№" + str(task.id)))
    kb.adjust(5)
    kb.row(InlineKeyboardButton(text="↩️Назад", callback_data="student_tasks"))
    return kb.as_markup(resize_keyboard=True)
