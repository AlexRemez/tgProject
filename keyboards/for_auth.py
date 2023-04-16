from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from db.connect import async_db_session
from db.models import User


def auth() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(text="Зарегистрироваться", callback_data="auth"))
    kb.add(InlineKeyboardButton(text="Отмена", callback_data="AuthCancel"))
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)


def telephone() -> ReplyKeyboardBuilder:
    kb = ReplyKeyboardBuilder()
    kb.add(KeyboardButton(text="Отправить номер", request_contact=True))
    return kb.as_markup(resize_keyboard=True, one_time_keyboard=True, is_persistent=True)


def status() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(text="Тренер", callback_data="status.coach"))
    kb.add(InlineKeyboardButton(text="Ученик", callback_data="status.student"))
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)


def confirm() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(text="Всё верно", callback_data="good"))
    kb.add(InlineKeyboardButton(text="Что-то не так", callback_data="AuthCancel"))
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)