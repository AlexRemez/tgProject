from random import randint

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

import bot
from aiogram import Router, types, F, Bot
from aiogram.filters import Command, CommandObject, Text, callback_data

from aiogram.types import FSInputFile, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from db.connect import async_db_session
from db.models import Exercises
from handlers.profile import Profile, save_previous
from keyboards.for_list_exercises import list_ex_kb
from keyboards.for_profile import confirm_kb, student_confirm_kb

router_1 = Router()

PATH_TO_IMAGES = 'images/'


class ExerciseState(StatesGroup):
    list_drills = State()


@router_1.message(Command('list_drills'))
async def show_drills(message: types.Message, bot: Bot, state: FSMContext):
    keyboard = await list_ex_kb()
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    await message.answer('Выберите номер упражнения!', reply_markup=keyboard)


@router_1.callback_query(Text(startswith="№"))
async def show_drill(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    ex_id = int(callback.data[1:])
    exercise = await Exercises.get(id=ex_id)
    print(f"Номер упражнения - {ex_id}")

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
        await callback.message.answer(f'<b>Упражнение {exercise.id}:</b><i>{description}</i>{rules}',
                                      parse_mode="HTML")
        now_state = await state.get_state()
        if now_state == Profile.confirm:
            await save_previous(state, callback, Profile.confirm)
            await state.update_data(confirm_task_id=ex_id)
            await callback.message.answer_photo(img, reply_markup=confirm_kb())
            await state.set_state(Profile.show_exercise)
            await callback.answer()
        elif now_state == Profile.student_confirm:
            await save_previous(state, callback, Profile.student_confirm)
            await state.update_data(confirm_task_id=ex_id)
            await callback.message.answer_photo(img, reply_markup=student_confirm_kb())
            await state.set_state(Profile.show_exercise)
            await callback.answer()
        else:
            await callback.message.answer_photo(img)


@router_1.message(Command('show_all_drills'))
async def show_all_drills(message: types.Message, bot: Bot):
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    exercises = await Exercises.all()
    print(f"Количество упражнений: {len(exercises)}")
    for exercise in exercises:
        img = FSInputFile(PATH_TO_IMAGES + exercise.path)
        if exercise.description:
            description = f'\n{exercise.description}'
        else:
            description = ''
        if exercise.rules:
            rules = f'\nПравила выполнения:\n{exercise.rules}'
        else:
            rules = ''
        await message.answer(f'<b>Упражнение {exercise.id}:</b><i>{description}</i>{rules}',
                             parse_mode="HTML")
        await message.answer_photo(img)
