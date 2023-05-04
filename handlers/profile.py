import datetime

from aiogram import Router, Bot, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove, Update
from aiogram.filters import Command, Text

from db.models import Coaches, Students, Tasks
from filters.in_range_ex import ValidExerciseFilter
from keyboards.for_add_exercises import add_exercise
from keyboards.for_list_exercises import list_ex_tasks, student_confirm_task_kb
from keyboards.for_profile import student_list_kb, coach_services, back, tasks_list_kb, add_task, \
    student_services, student_tasks_list_kb, delete_account_kb

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
    coach_profile = State()
    student_profile = State()
    students_list = State()
    student_info = State()
    check_tasks = State()
    confirm = State()
    show_exercise = State()
    add_task = State()
    coach_info = State()
    student_confirm = State()


@profile_router.message(Command("profile"))
async def check_profile(message: Message, state: FSMContext):
    await message.delete()
    student = await Students.get(tg_id=message.from_user.id)
    coach = await Coaches.get(tg_id=message.from_user.id)
    await state.update_data(previous_messages=[])
    if coach:
        await state.set_state(Profile.coach_profile)
        students_list = await Students.filter(coach_id=coach.id)
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
        await state.set_state(Profile.student_profile)
        coach = await Coaches.get(id=student.coach_id)
        if coach:
            coach_name = coach.first_name
        else:
            coach_name = "Нет тренера"
        await message.answer(
            f"\
            <b>!Ваш профиль !</b>\
            \nНикнейм: {student.first_name}\
            \nНомер телефона: {student.telephone}\
            \nВаш тренер: {coach_name}\
            \nДата регистрации профиля: {student.date_auth}\
            ",
            parse_mode="HTML",
            reply_markup=student_services()
        )
    else:
        await message.answer("<b>Вы не зарегистрированы!</b>", parse_mode="HTML", reply_markup=None)


@profile_router.callback_query(Profile.coach_profile, Text(text="my_students"))
async def students_list(callback: CallbackQuery, bot: Bot, state: FSMContext):
    await save_previous(state, callback, Profile.coach_profile)
    await state.set_state(Profile.students_list)
    coach = await Coaches.get(tg_id=callback.from_user.id)
    print(coach)
    keyboard = await student_list_kb(coach)
    await callback.message.edit_text("👥<b>Ваши ученики</b>👥", parse_mode="HTML", reply_markup=keyboard)
    await callback.answer()


@profile_router.callback_query(Profile.students_list, Text(startswith="#"))
async def student_info(callback: CallbackQuery, state: FSMContext):
    await save_previous(state, callback, Profile.students_list)
    await state.set_state(Profile.student_info)
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
async def back_handler(callback: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    previous_messages: list = data['previous_messages']
    previous_message = previous_messages[-1]
    previous_state = previous_message['previous_message_state']
    now_state = await state.get_state()
    await state.set_state(previous_state)
    previous_messages.pop()
    if now_state == Profile.show_exercise:
        await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id - 1)
        await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
        await callback.message.answer(text=previous_message['previous_message_text'],
                                      reply_markup=previous_message['previous_message_kb'],
                                      parse_mode="HTML")
        await state.update_data(confirm_task_id=None)
    else:
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


@profile_router.callback_query(Text("tasks"), Profile.coach_profile)
async def tasks_list(callback: CallbackQuery, state: FSMContext):
    await save_previous(state, callback, Profile.coach_profile)
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
    await callback.message.edit_text(text=tasks_message, parse_mode="HTML", reply_markup=add_task())
    await state.set_state(Profile.add_task)


@profile_router.callback_query(Text("add_task"), Profile.add_task)
async def add_task_1(callback: CallbackQuery, state: FSMContext):
    await save_previous(state, callback, Profile.add_task)
    coach = await Coaches.get(tg_id=callback.from_user.id)
    keyboard = await student_list_kb(coach)
    await callback.message.edit_text(
        text="<b>Выберите ученика</b>",
        parse_mode="HTML",
        reply_markup=keyboard
    )


@profile_router.callback_query(Profile.add_task, Text(startswith="#"))
async def add_task_2(callback: CallbackQuery, state: FSMContext):
    await save_previous(state, callback, Profile.add_task)
    student_id = int(callback.data[1:])
    await state.update_data(student_id=student_id)
    await callback.message.edit_text(
        text="<b>Введите номер упражнения вручную</b>",
        parse_mode="HTML",
        reply_markup=back()
    )


@profile_router.message(Profile.add_task, ValidExerciseFilter())
async def add_confirm(message: Message, state: FSMContext, bot: Bot):
    print("good")
    data = await state.get_data()
    print(message.text)
    await Tasks.create(
        exercise_id=int(message.text),
        student_id=data['student_id']
    )
    await state.clear()
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    await message.answer(text="<b>Задача добавлена!</b>", parse_mode="HTML")


@profile_router.callback_query(Text("waiting_confirm"), Profile.check_tasks)
async def students_confirm_list(callback: CallbackQuery, state: FSMContext):
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
    tasks_message += "\n==================================\n⬇️<i>Выберите ученика</i>⬇️"
    keyboard = await student_list_kb(coach)
    await callback.message.edit_text(text=tasks_message, parse_mode="HTML", reply_markup=keyboard)
    await state.set_state(Profile.confirm)


@profile_router.callback_query(Profile.confirm, Text(startswith="#"))
async def student_confirm_list(callback: CallbackQuery, state: FSMContext):
    await save_previous(state, callback, Profile.confirm)
    student: Students = await Students.get(id=int(callback.data[1:]))
    tasks = await Tasks.filter(student_id=student.id, student_status=True, coach_status=False)
    tasks_message = f"<b>Список задач {student.first_name}</b>\n"
    for task in tasks:
        task: Tasks
        tasks_message += f"Упр. №{task.exercise_id} | <i>ожидает подтверждения!</i>\n"
    keyboard = await list_ex_tasks(tasks)
    await state.update_data(confirm_student=student)
    await callback.message.edit_text(text=tasks_message, parse_mode="HTML", reply_markup=keyboard)


@profile_router.callback_query(Text(text="confirm"), Profile.show_exercise)
async def confirm(callback: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    confirm_student: Students
    confirm_student, confirm_task_ex_id = data['confirm_student'], data['confirm_task_id']
    print(confirm_student.first_name, confirm_task_ex_id)

    task: Tasks = await Tasks.get(student=confirm_student, exercise_id=confirm_task_ex_id)
    await task.update(coach_status=True, date_update_coach=str(datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")))
    await callback.answer("Задача подтверждена!")
    await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id - 1)
    await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
    await state.clear()


@profile_router.callback_query(Text(text="my_coach"), Profile.student_profile)
async def my_coach(callback: CallbackQuery, state: FSMContext):
    await save_previous(state, callback, Profile.student_profile)
    await state.set_state(Profile.coach_info)
    student = await Students.get(tg_id=callback.from_user.id)
    coach: Coaches = student.coach
    if coach:
        await callback.message.edit_text(
            text=f"\
                <b>!Профиль тренера!</b>\
                \nНикнейм: {coach.first_name}\
                \nНомер телефона: {coach.telephone}\
                \nДата регистрации профиля: {coach.date_auth}\
                ",
            parse_mode="HTML",
            reply_markup=back()
        )
    else:
        await callback.message.edit_text(
            text="<b>У вас нет тренера!</b>",
            parse_mode="HTML",
            reply_markup=back()
        )


@profile_router.callback_query(Text("tasks"), Profile.student_profile)
async def tasks_list(callback: CallbackQuery, state: FSMContext):
    await save_previous(state, callback, Profile.student_profile)
    await callback.message.edit_reply_markup(inline_message_id=callback.inline_message_id,
                                             reply_markup=student_tasks_list_kb())
    await state.set_state(Profile.check_tasks)


@profile_router.callback_query(Text("student_completed_tasks"), Profile.check_tasks)
async def completed_tasks(callback: CallbackQuery, state: FSMContext):
    await save_previous(state, callback, Profile.check_tasks)
    student = await Students.get(tg_id=callback.from_user.id)
    tasks = await Tasks.filter(student_id=student.id, coach_status=True, student_status=True)
    tasks_message = "<b>Список выполненых упражнений</b>\n"
    num = 0
    for task in tasks:
        task: Tasks
        num += 1
        tasks_message += f"{num}) №{task.id} | Дата выполнения: {task.date_update_student}\n"
    await callback.message.edit_text(text=tasks_message, parse_mode="HTML", reply_markup=back())


@profile_router.callback_query(Text("student_process_tasks"), Profile.check_tasks)
async def process_tasks(callback: CallbackQuery, state: FSMContext):
    await save_previous(state, callback, Profile.check_tasks)
    student = await Students.get(tg_id=callback.from_user.id)
    await state.update_data(confirm_student=student)
    tasks = await Tasks.filter(student_id=student.id, coach_status=False)
    tasks_message = "<b>Список текущих задач</b>\n"
    num = 0
    for task in tasks:
        task: Tasks
        num += 1
        if task.student_status:
            status = "<i>Ожидает подтверждения</i>"
        else:
            status = "<i>В процессе</i>"
        tasks_message += f"{num}) №{task.exercise_id} |  {status}\n"
    tasks_message += "\n==================================" \
                     "\n⬇️Выберите упражнение для подтверждения⬇️"
    await state.set_state(Profile.student_confirm)
    keyboard = await student_confirm_task_kb(student)
    await callback.message.edit_text(text=tasks_message, parse_mode="HTML", reply_markup=keyboard)


@profile_router.callback_query(Text(text="student_confirm"), Profile.show_exercise)
async def student_confirm(callback: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    confirm_student: Students
    confirm_student, confirm_task_ex_id = data['confirm_student'], data['confirm_task_id']
    print(confirm_student.first_name, confirm_task_ex_id)

    task: Tasks = await Tasks.get(student=confirm_student, exercise_id=confirm_task_ex_id)
    await task.update(student_status=True, date_update_student=str(datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")))
    await callback.answer("Задача подтверждена!", show_alert=True)
    await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id - 1)
    await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
    await state.clear()


@profile_router.callback_query(Text(text="confirm_delete"))
async def confirm_delete_account(callback: CallbackQuery, state: FSMContext):
    await save_previous(state, callback, Profile.student_profile)
    text = f"<b>ВЫ УВЕРЕНЫ?</b>" \
           f"\n<i>После удаления вы потеряете все данные связанные с вашим аккаунтом без воможности восстановления!</i>" \
           f"\n<i>Вы не сможете просмотреть результаты своих тренировок!</i>"
    await callback.message.edit_text(text=text, parse_mode="HTML", reply_markup=delete_account_kb())


@profile_router.callback_query(Text(text="delete_account"))
async def delete_account(callback: CallbackQuery, state: FSMContext):
    student = await Students.get(tg_id=callback.from_user.id)
    coach = await Coaches.get(tg_id=callback.from_user.id)
    if student:
        await student.delete()
        print("Аккаунт студента удален!")
    elif coach:
        await coach.delete()
        print("Аккаунт тренера удален!")
    await state.clear()
    await callback.answer("Ваш аккаунт удалён!", show_alert=True)
    await callback.message.delete()


@profile_router.callback_query(Text(text="del_cancel"))
async def cancel_delete(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.delete()





