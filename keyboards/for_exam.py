from _ast import In

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from db.models import Tags, Exercises


def exam_alert_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.row(
        InlineKeyboardButton(text="😨Я боюсь", callback_data="main_menu"),
        InlineKeyboardButton(text="Я готов🤜🤛", callback_data="exam_choose_ex")
    )
    return kb.as_markup(resize_keyboard=True)


def exam_ex_level_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text="level 1", callback_data="level-1"),
           InlineKeyboardButton(text="level 2", callback_data="level-2"),
           InlineKeyboardButton(text="level 3", callback_data="level-3"))
    kb.row(InlineKeyboardButton(text="level 4", callback_data="level-4"),
           InlineKeyboardButton(text="level 5", callback_data="level-5"))
    kb.row(InlineKeyboardButton(text="Отмена", callback_data="main_menu"))
    return kb.as_markup(resize_keyboard=True)


def exam_ex_num_kb(ex_list) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for ex in ex_list:
        ex: Exercises
        kb.add(InlineKeyboardButton(text=str(ex.id), callback_data="exam_ex_num-" + str(ex.id)))
    kb.adjust(4)
    kb.row(InlineKeyboardButton(text="↩️Назад", callback_data="exam_choose_ex"))
    return kb.as_markup(resize_keyboard=True)


def exam_choose_confirm(level) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text="🤩Хочу это", callback_data="exam_choose_ex_confirm"))
    kb.row(InlineKeyboardButton(text="↩️Назад", callback_data=level))
    return kb.as_markup(resize_keyboard=True)


def exam_notify(exam_id) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text="👀Посмотреть", callback_data="check_exam-" + str(exam_id)))
    return kb.as_markup(resize_keyboard=True)


def start_exam() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text="🔥Бросить вызов🔥", callback_data="exam"))
    return kb.as_markup(resize_keyboard=True)


def exam_access_kb(exam_id) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text="❌Отклонить", callback_data="exam_forbid-" + exam_id),
           InlineKeyboardButton(text="✅Разрешить", callback_data="exam_access-" + exam_id))
    kb.row(InlineKeyboardButton(text="✖️Отложить✖️", callback_data="hide_message"))
    return kb.as_markup(resize_keyboard=True)


def my_exam_kb(exam_id, continue_exam=False) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    if continue_exam:
        ps = "-admin"
    else:
        ps = ""
    kb.row(InlineKeyboardButton(text="🔥Мой экзамен", callback_data="check_exam-" + exam_id + ps))
    return kb.as_markup(resize_keyboard=True)


def exam_preparation_kb(exam_id) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text="Следующий шаг➡️", callback_data="preparation_cam-" + exam_id))
    return kb.as_markup(resize_keyboard=True)


def start_exam_kb(exam_id) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text="⏳Начать экзамен", callback_data="start_exam-" + exam_id))
    return kb.as_markup(resize_keyboard=True)


def exam_attempt_kb(exam_id, attempt=None) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    attempt = f"-{attempt}"
    kb.row(InlineKeyboardButton(text="❌Была ошибка", callback_data="start_exam-" + exam_id + attempt + "-bad"),
           InlineKeyboardButton(text="✅Удачно", callback_data="start_exam-" + exam_id + attempt + "-good"))
    return kb.as_markup(resize_keyboard=True)
