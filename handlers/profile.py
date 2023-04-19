from aiogram import Router, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove, Update
from aiogram.filters import Command, Text

from db.models import Coaches, Students, Tasks
from keyboards.for_add_exercises import add_exercise
from keyboards.for_list_exercises import list_ex_tasks
from keyboards.for_profile import student_list_kb, coach_services, back, tasks_list_kb, waiting_confirm_kb

profile_router = Router()


async def save_previous(state: FSMContext, callback: CallbackQuery, new_state):
    new_message = {'previous_message_text': callback.message.text,
                   'previous_message_kb': callback.message.reply_markup,
                   'previous_message_state': new_state}
    previous_messages = await state.get_data()
    previous_messages: list = previous_messages['previous_messages']
    previous_messages.append(new_message)
    await state.update_data(previous_messages=previous_messages)


class Profile(StatesGroup):
    profile = State()
    students_list = State()
    student = State()
    check_tasks = State()
    more_tasks = State()


@profile_router.message(Command("profile"))
async def check_profile(message: Message, bot: Bot, state: FSMContext):
    await state.set_state(Profile.profile)
    student = await Students.get(tg_id=message.from_user.id)
    coach = await Coaches.get(tg_id=message.from_user.id)
    await state.update_data(previous_messages=[])
    if coach:
        students_list = await Students.all()
        await message.answer(
            f"\
            <b>!Ваш профиль тренера!</b>\
            \nНикнейм: {coach.first_name}\
            \nНомер телефона: {coach.telephone}\
            \nКоличество учеников: {len(students_list)}\
            \nДата регистрации профиля: {coach.date_auth}\
            ",
            parse_mode="HTML",
            reply_markup=coach_services()
        )
    elif student:
        coach = await Coaches.get(id=student.coach_id)
        await message.answer(
            f"\
            <b>!Ваш профиль !</b>\
            \nНикнейм: {student.first_name}\
            \nНомер телефона: {student.telephone}\
            \nВаш тренер: {coach.first_name}\
            \nДата регистрации профиля: {student.date_auth}\
            ",
            parse_mode="HTML",
            reply_markup=None
        )
    else:
        await message.answer("<b>Вы не зарегистрированы!</b>", parse_mode="HTML", reply_markup=None)


@profile_router.callback_query(Profile.profile, Text(text="my_students"))
async def students_list(callback: CallbackQuery, bot: Bot, state: FSMContext):
    await save_previous(state, callback, Profile.profile)
    await state.set_state(Profile.students_list)
    coach = await Coaches.get(tg_id=callback.from_user.id)
    print(coach)
    keyboard = await student_list_kb(coach)
    await callback.message.edit_text("👥<b>Ваши ученики</b>👥", parse_mode="HTML", reply_markup=keyboard)
    await callback.answer()


@profile_router.callback_query(Profile.students_list, Text(startswith="#"))
async def student(callback: CallbackQuery, state: FSMContext):
    await save_previous(state, callback, Profile.students_list)
    await state.set_state(Profile.student)
    student_profile = await Students.get(id=int(callback.data[1:]))
    await callback.message.edit_text(
        text=f"\
            <b>!Профиль ученика!</b>\
            \nНикнейм: {student_profile.first_name}\
            \nНомер телефона: {student_profile.telephone}\
            \nТренер: {student_profile.coach.first_name}\
            \nДата регистрации профиля: {student_profile.date_auth}\
            ",
        parse_mode="HTML",
        reply_markup=back()
    )


@profile_router.callback_query(Text(text="back"))
async def back_handler(callback: CallbackQuery, state: FSMContext):
    previous_messages = await state.get_data()
    previous_messages: list = previous_messages['previous_messages']
    previous_message = previous_messages[-1]
    previous_state = previous_message['previous_message_state']
    await state.set_state(previous_state)
    previous_messages.pop()

    await callback.message.edit_text(text=previous_message['previous_message_text'],
                                     reply_markup=previous_message['previous_message_kb'],
                                     parse_mode="HTML")
    await state.update_data(previous_messages=previous_messages)


@profile_router.callback_query(Text("add_exercise"))
async def add_ex(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
    await callback.message.answer('<b>Добавьте свое упражнение выполнив 3 простых шага!</b>',
                                  parse_mode="HTML",
                                  reply_markup=add_exercise())
    await state.clear()
    await callback.answer()


@profile_router.callback_query(Text("tasks"), Profile.profile)
async def tasks(callback: CallbackQuery, state: FSMContext):
    await save_previous(state, callback, Profile.profile)
    await callback.message.edit_reply_markup(inline_message_id=callback.inline_message_id,
                                             reply_markup=tasks_list_kb())
    await state.set_state(Profile.check_tasks)


@profile_router.callback_query(Text("completed_tasks"), Profile.check_tasks)
async def completed_tasks(callback: CallbackQuery, state: FSMContext):
    await save_previous(state, callback, Profile.check_tasks)
    coach = await Coaches.get(tg_id=callback.from_user.id)
    students = await Students.filter(coach_id=coach.id)
    tasks_message = "<b>Список выполненых задач</b>\n"
    num = 0
    for student in students:
        student: Students
        num += 1
        tasks = await Tasks.filter(student_id=student.id, student_status=True, coach_status=True)

        tasks_message += f"{num}) {student.first_name} | Кол-во выполненых задач: {len(tasks)}\n"

    await callback.message.edit_text(text=tasks_message, parse_mode="HTML", reply_markup=back())
    await callback.answer()


@profile_router.callback_query(Text("process_tasks"), Profile.check_tasks)
async def process_tasks(callback: CallbackQuery, state: FSMContext):
    await save_previous(state, callback, Profile.check_tasks)
    coach = await Coaches.get(tg_id=callback.from_user.id)
    students = await Students.filter(coach_id=coach.id)
    tasks_message = "<b>Список текущих задач</b>\n"
    num = 0
    for student in students:
        student: Students
        num += 1
        tasks = await Tasks.filter(student_id=student.id, student_status=False, coach_status=False)
        tasks_message += f"{num}) {student.first_name} | Задач в процессе: {len(tasks)}\n"
    await callback.message.edit_text(text=tasks_message, parse_mode="HTML", reply_markup=back())


@profile_router.callback_query(Text("waiting_confirm"), Profile.check_tasks)
async def process_tasks(callback: CallbackQuery, state: FSMContext):
    await save_previous(state, callback, Profile.check_tasks)
    coach = await Coaches.get(tg_id=callback.from_user.id)
    students = await Students.filter(coach_id=coach.id)
    tasks_message = "<b>Список задач для подтверждения</b>\n"
    num = 0
    for student in students:
        student: Students
        num += 1
        tasks = await Tasks.filter(student_id=student.id, student_status=True, coach_status=False)
        tasks_message += f"{num}) {student.first_name} | Ожидают подтверждения: {len(tasks)}\n"

    await callback.message.edit_text(text=tasks_message, parse_mode="HTML", reply_markup=waiting_confirm_kb())
    await state.set_state(Profile.more_tasks)


@profile_router.callback_query(Text("more"), Profile.more_tasks)
async def process_tasks(callback: CallbackQuery, state: FSMContext):
    await save_previous(state, callback, Profile.more_tasks)
    coach = await Coaches.get(tg_id=callback.from_user.id)
    tasks_message = "<b>Выберите ученика</b>"
    keyboard = await student_list_kb(coach)
    await callback.message.edit_text(text=tasks_message, parse_mode="HTML", reply_markup=keyboard)


@profile_router.callback_query(Profile.more_tasks, Text(startswith="#"))
async def student(callback: CallbackQuery, state: FSMContext):
    await save_previous(state, callback, Profile.more_tasks)
    student: Students = await Students.get(id=int(callback.data[1:]))
    tasks = await Tasks.filter(student_id=student.id)
    tasks_message = f"<b>Список задач {student.first_name}</b>\n"
    for task in tasks:
        task: Tasks
        tasks_message += f"Упр. №{task.exercise_id} | <i>ожидает подтверждения!</i>\n"
    keyboard = await list_ex_tasks(tasks)
    await callback.message.edit_text(text=tasks_message, parse_mode="HTML", reply_markup=keyboard)





