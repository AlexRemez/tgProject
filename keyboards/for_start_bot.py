from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def main_buttons_kb() -> ReplyKeyboardBuilder:
    kb = ReplyKeyboardBuilder()
    kb.add(KeyboardButton(text="⭐️Меню"))
    return kb.as_markup(resize_keyboard=True, is_persistent=True)