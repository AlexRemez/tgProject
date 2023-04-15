from random import randint

from aiogram import Router, types, F
from aiogram.filters import Command, CommandObject, Text, callback_data

from aiogram.types import FSInputFile, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from db.connect import async_db_session
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
    keyboard = await list_ex_kb()
    await message.answer('Выберите номер упражнения!', reply_markup=keyboard)


@router_1.message(Command('show_all_drills'))
async def show_all_drills(message: types.Message):
    async with async_db_session() as session:
        exercises = await session.execute(select(Exercises))
        exercises = exercises.fetchall()
    print(exercises)
    for exercise in exercises:
        exercise: Exercises = exercise[0]
        img = FSInputFile(PATH_TO_IMAGES + exercise.path)
        if exercise.description:
            description = f'\n{exercise.description}'
        else:
            description = ''
        if exercise.rules:
            rules = f'\nПравила выполнения:\n{exercise.rules}'
        else:
            rules = ''
        print(img)
        await message.answer(f'<b>Упражнение {exercise.ex_num}:</b><i>{description}</i>{rules}',
                             parse_mode="HTML")
        await message.answer_photo(img)


@router_1.callback_query(Text(startswith="№"))
async def show_drill(callback: CallbackQuery):
    async with async_db_session() as session:
        ex_num = callback.data[1:]
        print(ex_num)
        exercise = await session.execute(select(Exercises).where(Exercises.ex_num == int(ex_num)))
        exercise = exercise.first()
        print(exercise)
        exercise = exercise[0]

    if exercise is None:
        await callback.message.answer('<b>Error</b>', parse_mode="HTML")
    else:
        img = FSInputFile(PATH_TO_IMAGES + exercise.path)
        if exercise.description:
            description = f'\n{exercise.description}'
        else:
            description = ''
        if exercise.rules:
            rules = f'\nПравила выполнения:\n{exercise.rules}'
        else:
            rules = ''
        await callback.message.answer(f'<b>Упражнение {exercise.ex_num}:</b><i>{description}</i>{rules}',
                                      parse_mode="HTML")
        await callback.message.answer_photo(img)
        await callback.answer()
