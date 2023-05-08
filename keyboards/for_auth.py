from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from db.models import Coaches


def auth() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(text="Зарегистрироваться", callback_data="auth"))
    kb.add(InlineKeyboardButton(text="Отмена", callback_data="AuthCancel"))
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)


def telephone() -> ReplyKeyboardBuilder:
    kb = ReplyKeyboardBuilder()
    kb.add(KeyboardButton(text="Отправить номер", request_contact=True))
    kb.add(KeyboardButton(text="Пропустить"))
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


async def coach_list() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    coaches = await Coaches.all()
    for coach in coaches:
        kb.add(InlineKeyboardButton(text=f"{coach.first_name}", callback_data=str(coach.id)))
    kb.adjust(2)
    kb.row(InlineKeyboardButton(text="↩️Назад", callback_data="profile"))
    return kb.as_markup(resize_keyboard=True)
