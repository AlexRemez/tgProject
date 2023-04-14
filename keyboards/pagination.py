from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from db.models import Exercises


def list_ex_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for ex_num in exercises_num:
        kb.add(InlineKeyboardButton(text="№" + str(ex_num[0]), callback_data="№" + str(ex_num[0])))
    kb.adjust(4)
    return kb.as_markup(resize_keyboard=True)