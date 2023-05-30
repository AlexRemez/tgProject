from aiogram.types import KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


def main_buttons_kb() -> ReplyKeyboardBuilder:
    kb = ReplyKeyboardBuilder()
    kb.add(KeyboardButton(text="⭐️Меню"))
    return kb.as_markup(resize_keyboard=True, is_persistent=True)


def back_menu_kb(text="⭐️Меню"):
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text=text, callback_data="main_menu"))
    return kb.as_markup(resize_keyboard=True)
