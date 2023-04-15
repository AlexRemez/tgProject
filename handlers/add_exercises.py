from aiogram import Router, F, Bot
from aiogram.filters import Command, Text
from aiogram.fsm.context import FSMContext
from sqlalchemy import create_engine, select, func, insert
from sqlalchemy.orm import sessionmaker

from db.connect import async_db_session
from db.models import Exercises
from keyboards.for_add_exercises import add_exercise, add_any, add_rules, add_description, check_ex, last_step
from aiogram.types import CallbackQuery, Message, FSInputFile
from aiogram.fsm.state import StatesGroup, State
from handlers.start_bot import make_start_message
import os

router_3 = Router()


class NewExercise(StatesGroup):
    input_photo = State()
    input_rules = State()
    input_decription = State()
    last_step = State()


@router_3.message(Command("add_exercise"))
async def cmd_start(message: Message):
    await message.answer('<b>Добавьте свое упражнение выполнив 3 простых шага!</b>',
                         parse_mode="HTML",
                         reply_markup=add_exercise())


@router_3.callback_query(Text(text="1 step"))
async def step_1(callback: CallbackQuery, state: FSMContext):
    print('1 step')
    await callback.message.answer('<i>Пришлите изображение упражнения!</i>', reply_markup=add_any(), parse_mode="HTML")
    await state.set_state(NewExercise.input_photo)
    await callback.answer()


@router_3.message(F.photo, NewExercise.input_photo)
async def save_photo(message: Message, bot: Bot, state: FSMContext):
    async with async_db_session() as session:
        result = await session.execute(func.max(Exercises.id))
        ex_id = result.scalar() + 1
    path = f"drill_{ex_id}.png"
    print(path)
    await bot.download(
        message.photo[-1],
        destination=f"images/{path}"
    )
    await state.update_data(path=path)
    await state.update_data(id=ex_id)
    await state.update_data(name="Упражнение")
    await message.answer("<b>Фото успешно сохранено!</b>\n<i>Переходи ко второму шагу!</i>",
                         parse_mode="HTML",
                         reply_markup=add_rules())
    await state.set_state(NewExercise.input_rules)


@router_3.message(F.document, NewExercise.input_photo)
async def invalid_document(message: Message):
    await message.answer(text="Пришлите фото!")


@router_3.callback_query(Text(text="2 step"), NewExercise.input_rules)
async def step_2(callback: CallbackQuery):
    print('2 step')
    await callback.message.answer('<i>Напишите правила выполнения упражнения!</i>', reply_markup=add_any(),
                                  parse_mode="HTML")
    await callback.answer()


@router_3.message(Text, NewExercise.input_rules)
async def save_rules(message: Message, state: FSMContext):
    print('2 step')
    await state.update_data(rules=message.text)
    await message.answer("<b>Правила сохранены!</b>\n<i>Переходи к 3 шагу!</i>", reply_markup=add_description(),
                         parse_mode="HTML")
    await state.set_state(NewExercise.input_decription)


@router_3.callback_query(Text(text="3 step"), NewExercise.input_decription)
async def step_3(callback: CallbackQuery):
    print('3 step')
    await callback.message.answer(
        '<i>Напишите описание(Какой сложности упражнение? Какие технические элементы развивает?)!</i>',
        reply_markup=add_any(),
        parse_mode="HTML")
    await callback.answer()


@router_3.message(Text, NewExercise.input_decription)
async def save_description(message: Message, state: FSMContext):
    print('3 step')
    await state.update_data(description=message.text)
    await message.answer("<b>Описание сохранено!</b>\n<i>Теперь проверьте введенные данные.</i>",
                         reply_markup=check_ex(),
                         parse_mode="HTML")
    await state.set_state(NewExercise.last_step)


@router_3.callback_query(Text(text="check"), NewExercise.last_step)
async def check(callback: CallbackQuery, state: FSMContext):
    print('check')
    user_exercise = await state.get_data()
    await callback.message.answer("<b>Ваше упражнение:</b>", parse_mode="HTML")

    img = FSInputFile(f"images/{user_exercise['path']}")
    print(img)
    if user_exercise['description']:
        description = f'\n{user_exercise["description"]}'
    else:
        description = ''
    if user_exercise['rules']:
        rules = f'\nПравила выполнения:\n{user_exercise["rules"]}'
    else:
        rules = ''
    await callback.message.answer(f'<b>Упражнение {user_exercise["id"]}:</b><i>{description}</i>{rules}',
                                  parse_mode="HTML")
    await callback.message.answer_photo(img, reply_markup=last_step())


@router_3.callback_query(Text(text="send"), NewExercise.last_step)
async def save_exercise(callback: CallbackQuery, state: FSMContext):
    print('send to db')

    user_exercise = await state.get_data()
    with async_db_session() as session:
        await session.execute(insert(Exercises).values(
            name=user_exercise['name'],
            path=user_exercise['path'],
            description=user_exercise['description'],
            rules=user_exercise['rules']
        ))
        await session.commit()

    async with async_db_session() as session:
        result = await session.execute(func.max(Exercises.id))
        ex_id = result.scalar()
        await callback.answer(
            text=f"Ваше упражнение сохранено!\nНомер упражнения: {ex_id}",
            show_alert=True
        )
    await state.clear()
    await callback.message.answer(make_start_message(callback), parse_mode="HTML")


@router_3.callback_query(Text(text="Cancel"))
async def cancel(callback: CallbackQuery, state: FSMContext):
    print('cancel')
    user_exercise = await state.get_data()
    if "path" in user_exercise:
        file_path = f"images/{user_exercise['path']}"
        # проверяем, существует ли файл
        if os.path.exists(file_path):
            # удаляем файл
            os.remove(file_path)
            print(f"Файл {file_path} успешно удален.")
        else:
            print(f"Файл {file_path} не существует.")
    await state.clear()
    await callback.message.answer(make_start_message(callback), parse_mode="HTML")
    await callback.answer()
