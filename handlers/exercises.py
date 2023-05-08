from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from aiogram import Router, types, Bot
from aiogram.filters import Command, Text

from aiogram.types import FSInputFile, CallbackQuery

from db.models import Exercises, Tasks
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
    await message.delete()
    await message.answer('Выберите номер упражнения!', reply_markup=keyboard)


@router_1.callback_query(Text(text="list_drills"))
async def show_drills(callback: types.CallbackQuery):
    keyboard = await list_ex_kb()
    await callback.message.delete()
    await callback.message.answer('Выберите номер упражнения!', reply_markup=keyboard)


@router_1.callback_query(Text(startswith="№"))
async def show_drill(callback: CallbackQuery, state: FSMContext):
    # await callback.message.delete()
    now_state = await state.get_state()
    if now_state == Profile.confirm or now_state == Profile.student_confirm:
        await callback.message.delete()
        task_id = int(callback.data[1:])
        task: Tasks = await Tasks.get(id=task_id)
        ex_id = task.exercise_id
        print(task_id)
    else:
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
        data = await state.get_data()
        if now_state == Profile.confirm:
            await state.update_data(confirm_task_id=task_id)
            await callback.message.answer_photo(img,
                                                reply_markup=confirm_kb(previous_step=data['student_confirm_list']))
            await state.set_state(Profile.show_exercise)
            await callback.answer()
        elif now_state == Profile.student_confirm:
            await state.update_data(confirm_task_id=task_id)
            await callback.message.answer_photo(img, reply_markup=student_confirm_kb("student_process_tasks"))
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
