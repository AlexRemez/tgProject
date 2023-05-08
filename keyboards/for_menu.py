from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def main_menu_kb(auth: bool) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    if auth:
        profile_button = InlineKeyboardButton(text="👤Профиль", callback_data="profile")
    else:
        profile_button = InlineKeyboardButton(text="🟡Зарегистрироваться", callback_data="auth")
    kb.row(profile_button,
           InlineKeyboardButton(text="🎱Список упражнений", callback_data="list_drills"))
    kb.row(InlineKeyboardButton(text="✖️Скрыть меню✖️", callback_data="hide_menu"))
    return kb.as_markup(resize_keyboard=True)
