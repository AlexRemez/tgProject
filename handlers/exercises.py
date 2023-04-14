from random import randint

from aiogram import Router, types, F
from aiogram.filters import Command, CommandObject, Text, callback_data

from aiogram.types import FSInputFile, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.models import Exercises
from keyboards.for_list_exercises import list_ex_kb

router_1 = Router()

PATH_TO_IMAGES = 'images/'

# создаем соединение с базой данных
engine = create_engine('postgresql://alex:remak4kko@127.0.0.1:5432/tgBot')

# создаем объект сессии
Session = sessionmaker(bind=engine)

# создаем сессию


@router_1.message(Command('list_drills'))
async def show_drills(message: types.Message):
    await message.answer('Выберите номер упражнения!', reply_markup=list_ex_kb())


@router_1.message(Command('show_all_drills'))
async def show_all_drills(message: types.Message):
    session = Session()
    exercises_nums = session.query(Exercises.ex_num).all()
    print(exercises_nums)
    for exercises_num in exercises_nums:
        ex_num = int(exercises_num[0])
        # запрашиваем объект из базы данных по его id
        exercises: Exercises = session.query(Exercises).filter_by(ex_num=ex_num).first()
        img = FSInputFile(PATH_TO_IMAGES + exercises.path)
        if exercises.description:
            description = f'\n{exercises.description}'
        else:
            description = ''
        if exercises.rules:
            rules = f'\nПравила выполнения:\n{exercises.rules}'
        else:
            rules = ''
        print(img)
        await message.answer(f'<b>Упражнение {exercises.ex_num}:</b><i>{description}</i>{rules}',
                             parse_mode="HTML")
        await message.answer_photo(img)
        session.close()


@router_1.callback_query(Text(startswith="№"))
async def show_drill(callback: CallbackQuery):
    session = Session()
    ex_num = callback.data[1:]
    # запрашиваем объект из базы данных по его id
    exercises: Exercises = session.query(Exercises).filter_by(ex_num=ex_num).first()
    if exercises is None:
        await callback.message.answer('<b>Error</b>', parse_mode="HTML")
    else:
        img = FSInputFile(PATH_TO_IMAGES + exercises.path)
        if exercises.description:
            description = f'\n{exercises.description}'
        else:
            description = ''
        if exercises.rules:
            rules = f'\nПравила выполнения:\n{exercises.rules}'
        else:
            rules = ''
        await callback.message.answer(f'<b>Упражнение {exercises.ex_num}:</b><i>{description}</i>{rules}',
                                      parse_mode="HTML")
        await callback.message.answer_photo(img)
        await callback.answer()
        session.close()
