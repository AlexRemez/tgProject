from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from db.models import Exercises
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from math import ceil
from db.connect import async_db_session


# def list_ex_kb() -> InlineKeyboardMarkup:
#     session = async_db_session()
#     print(type(session))
#     exercises_num = session.execute(select(Exercises.ex_num))
#     print(exercises_num)
#     session.close()
#     kb = InlineKeyboardBuilder()
#     for ex_num in exercises_num:
#         kb.add(InlineKeyboardButton(text="№" + str(ex_num[0]), callback_data="№" + str(ex_num[0])))
#     kb.adjust(4)
#     return kb.as_markup(resize_keyboard=True)


async def list_ex_kb() -> InlineKeyboardMarkup:
    async with async_db_session() as session:
        exercises_num = await session.execute(select(Exercises.ex_num))
        ex_num_list = exercises_num.fetchall()

    kb = InlineKeyboardBuilder()
    for ex_num in ex_num_list:
        kb.add(InlineKeyboardButton(text="№" + str(ex_num[0]), callback_data="№" + str(ex_num[0])))
    kb.adjust(4)
    return kb.as_markup(resize_keyboard=True)

