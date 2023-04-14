from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from db.models import Exercises
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from math import ceil


engine = create_engine('postgresql://alex:remak4kko@127.0.0.1:5432/tgBot')
Session = sessionmaker(bind=engine)


def list_ex_kb() -> InlineKeyboardMarkup:
    session = Session()
    exercises_num = session.query(Exercises.ex_num).all()
    kb = InlineKeyboardBuilder()
    # кол-во страниц пагинации (если 5 упражнений, то 2 страницы)
    len_page = ceil(len(exercises_num) / 4)
    num_page = 1

    for ex_num in exercises_num:
        kb.add(InlineKeyboardButton(text="№" + str(ex_num[0]), callback_data="№" + str(ex_num[0])))
    kb.adjust(4)
    session.close()

    # kb.add(
    #     InlineKeyboardButton(text="←", callback_data="None"),
    #     InlineKeyboardButton(text=f"{num_page}/{len_page}", callback_data="None"),
    #     InlineKeyboardButton(text="→", callback_data="None")
    # )
    return kb.as_markup(resize_keyboard=True)
