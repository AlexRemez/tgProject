from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def add_exercise() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(text="1 ШАГ", callback_data="1 step"))
    kb.add(InlineKeyboardButton(text="Отмена", callback_data="AddCancel"))
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)


def add_any() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(text="Отмена", callback_data="AddCancel"))
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)


def add_rules() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(text="2 ШАГ", callback_data="2 step"))
    kb.add(InlineKeyboardButton(text="Отмена", callback_data="AddCancel"))
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)


def add_description() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(text="3 ШАГ", callback_data="3 step"))
    kb.add(InlineKeyboardButton(text="Отмена", callback_data="AddCancel"))
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)


def check_ex() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(text="Проверить данные!", callback_data="check"))
    kb.add(InlineKeyboardButton(text="Отмена", callback_data="AddCancel"))
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)


def last_step() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(text="Отправить боту!", callback_data="send"))
    kb.add(InlineKeyboardButton(text="Отмена", callback_data="AddCancel"))
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)









