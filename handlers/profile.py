import datetime

from aiogram import Router, Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Text

from db.models import Coaches, Students, Tasks
from filters.in_range_ex import ValidExerciseFilter
from keyboards.for_add_exercises import add_exercise
from keyboards.for_list_exercises import list_ex_tasks, student_confirm_task_kb
from keyboards.for_profile import student_list_kb, back, coach_tasks_list_kb, add_task, \
    student_tasks_list_kb, delete_account_kb, my_coach_kb, task_notification_kb

profile_router = Router()


async def save_previous(state: FSMContext, callback: CallbackQuery, new_state):
    new_message = {'previous_message_text': callback.message.text,
                   'previous_message_kb': callback.message.reply_markup,
                   'previous_message_state': new_state}
    previous_messages = await state.get_data()
    previous_messages: list = previous_messages['previous_messages']
    previous_messages.append(new_message)
    await state.update_data(previous_messages=previous_messages)


async def save_current_step(callback: CallbackQuery, state: FSMContext):
    current_step = callback.data
    pass


class Profile(StatesGroup):
    students_list = State()
    student_info = State()
    check_tasks = State()
    confirm = State()
    show_exercise = State()
    add_task = State()
    coach_info = State()
    student_confirm = State()


@profile_router.callback_query(Text(text="my_students"))
async def students_list(callback: CallbackQuery, bot: Bot, state: FSMContext):
    coach = await Coaches.get(tg_id=callback.from_user.id)
    print(coach)
    keyboard = await student_list_kb(coach, previous_step="profile")
    await callback.message.edit_text("👥<b>Ваши ученики</b>👥", parse_mode="HTML", reply_markup=keyboard)
    await callback.answer()


@profile_router.callback_query(Text(startswith="#"))
async def student_info(callback: CallbackQuery, state: FSMContext):
    student_profile = await Students.get(id=int(callback.data[1:]))
    await callback.message.edit_text(
        text=f"\
            👤<b>Профиль ученика</b>👤\
            \n⚪️Никнейм: {student_profile.first_name}\
            \n📱Номер телефона: {student_profile.telephone}\
            \n⚫️Тренер: {student_profile.coach.first_name}\
            \n📅Дата регистрации профиля: {student_profile.date_auth}\
            ",
        parse_mode="HTML",
        reply_markup=back("my_students")
    )


@profile_router.callback_query(Text(text="back"))
async def back_handler(callback: CallbackQuery, state: FSMContext, bot: Bot):
    pass


@profile_router.callback_query(Text(text="backk"))
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
    await callback.message.answer('<b>Добавьте свое упражнение выполнив 3 простых шага!</b>',
                                  parse_mode="HTML",
                                  reply_markup=add_exercise())
    await state.clear()
    await callback.answer()


@profile_router.callback_query(Text("coach_tasks"))
async def tasks_list(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(text="📂<b>Фильтр задач</b>📂",
                                     parse_mode="HTML",
                                     reply_markup=coach_tasks_list_kb())


@profile_router.callback_query(Text("coach_completed_tasks"))
async def completed_tasks(callback: CallbackQuery, state: FSMContext):
    coach = await Coaches.get(tg_id=callback.from_user.id)
    students = await Students.filter(coach_id=coach.id)
    tasks_message = "<b>Список выполненых задач</b>\n"
    num = 0
    for student in students:
        student: Students
        num += 1
        tasks = await Tasks.filter(student_id=student.id, student_status=True, coach_status=True)

        tasks_message += f"{num}) {student.first_name} | Кол-во выполненых задач: {len(tasks)}\n"

    await callback.message.edit_text(text=tasks_message,
                                     parse_mode="HTML",
                                     reply_markup=back(previous_step="coach_tasks"))
    await callback.answer()


@profile_router.callback_query(Text("coach_process_tasks"))
async def process_tasks(callback: CallbackQuery, state: FSMContext):
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


@profile_router.callback_query(Text("add_task"))
async def add_task_1(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    coach = await Coaches.get(tg_id=callback.from_user.id)
    keyboard = await student_list_kb(coach, previous_step="coach_process_tasks")
    await callback.message.edit_text(
        text="<b>Выберите ученика</b>",
        parse_mode="HTML",
        reply_markup=keyboard
    )
    await callback.answer()


@profile_router.callback_query(Text(startswith="&"))
async def add_task_2(callback: CallbackQuery, state: FSMContext):
    student_id = int(callback.data[1:])
    await state.update_data(student_id=student_id)
    await callback.message.edit_text(
        text="<b>Введите номер упражнения вручную</b>",
        parse_mode="HTML",
        reply_markup=back(previous_step="add_task")
    )
    await state.set_state(Profile.add_task)


@profile_router.message(Profile.add_task, ValidExerciseFilter())
async def add_confirm(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    if await Tasks.get(student_id=data['student_id'], exercise_id=int(message.text), coach_status=False):
        await message.answer("<b>❌Ученик уже делает это упражнение!</b>", parse_mode="HTML")
    else:
        await Tasks.create(
            exercise_id=int(message.text),
            student_id=data['student_id']
        )
        await message.answer(text="<b>Задача добавлена!</b>",
                             parse_mode="HTML",
                             reply_markup=back(previous_step="coach_process_tasks"))
        student = await Students.get(id=data['student_id'])
        await bot.send_message(chat_id=student.tg_id,
                               text="💬<b>У вас новая задача</b>💬",
                               parse_mode="HTML",
                               reply_markup=task_notification_kb())
        try:
            await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
        except TelegramBadRequest:
            print("Error")
        await message.delete()
        await state.clear()


@profile_router.callback_query(Text("coach_waiting_confirm"))
async def students_confirm_list(callback: CallbackQuery, state: FSMContext):
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
    keyboard = await student_list_kb(coach, previous_step="coach_tasks")
    await callback.message.edit_text(text=tasks_message, parse_mode="HTML", reply_markup=keyboard)


@profile_router.callback_query(Text(startswith="*"))
async def student_confirm_list(callback: CallbackQuery, state: FSMContext, bot: Bot):
    now_state = await state.get_state()
    if now_state == Profile.show_exercise:
        await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id - 1)
        await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
    await state.update_data(student_confirm_list=callback.data)
    student: Students = await Students.get(id=int(callback.data[1:]))
    tasks = await Tasks.filter(student_id=student.id, student_status=True, coach_status=False)
    tasks_message = f"<b>Список задач {student.first_name}</b>\n"
    num = 0
    list_tasks = []
    for task in tasks:
        num += 1
        task: Tasks
        tasks_message += f"{num})Упр. №{task.exercise_id} | <i>ожидает подтверждения!</i>\n"
        list_tasks.append((num, task.id))
    await state.update_data(list_tasks=list_tasks)
    keyboard = await list_ex_tasks(tasks, previous_step="coach_waiting_confirm")
    await state.update_data(confirm_student=student)
    await state.set_state(Profile.confirm)
    try:
        await callback.message.edit_text(text=tasks_message, parse_mode="HTML", reply_markup=keyboard)
    except TelegramBadRequest:
        await callback.message.answer(text=tasks_message, parse_mode="HTML", reply_markup=keyboard)


@profile_router.callback_query(Text(text="confirm"), Profile.show_exercise)
async def confirm(callback: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    confirm_student: Students
    confirm_student, confirm_task_id = data['confirm_student'], data['confirm_task_id']
    print(confirm_student.first_name, confirm_task_id)

    task: Tasks = await Tasks.get(student=confirm_student, id=confirm_task_id)
    await task.update(coach_status=True, date_update_coach=str(datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")))
    await callback.answer("Задача подтверждена!")
    await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id - 1)
    await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
    await state.clear()


@profile_router.callback_query(Text(text="my_coach"))
async def my_coach(callback: CallbackQuery, state: FSMContext):
    student = await Students.get(tg_id=callback.from_user.id)
    coach: Coaches = student.coach
    if coach:
        await callback.message.edit_text(
            text=f"\
                👤<b>Профиль тренера</b>👤\
                \n⚫️Никнейм: {coach.first_name}\
                \n📱Номер телефона: {coach.telephone}\
                \n📅Дата регистрации профиля: {coach.date_auth}\
                ",
            parse_mode="HTML",
            reply_markup=my_coach_kb(previous_step="profile")
        )
    else:
        await callback.message.edit_text(
            text="<b>У вас нет тренера!</b>",
            parse_mode="HTML",
            reply_markup=back(previous_step="profile")
        )


@profile_router.callback_query(Text("student_tasks"))
async def tasks_list(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(text="📂<b>Фильтр задач</b>📂",
                                     parse_mode="HTML",
                                     reply_markup=student_tasks_list_kb())


@profile_router.callback_query(Text("student_completed_tasks"))
async def completed_tasks(callback: CallbackQuery, state: FSMContext):
    student = await Students.get(tg_id=callback.from_user.id)
    tasks = await Tasks.filter(student_id=student.id, coach_status=True, student_status=True)
    tasks_message = "<b>Список выполненых упражнений</b>\n"
    num = 0
    for task in tasks:
        task: Tasks
        num += 1
        tasks_message += f"{num}) №{task.exercise_id} | Дата выполнения: {task.date_update_student}\n"
    await callback.message.edit_text(text=tasks_message, parse_mode="HTML", reply_markup=back("student_tasks"))


@profile_router.callback_query(Text("student_process_tasks"))
async def process_tasks(callback: CallbackQuery, state: FSMContext, bot: Bot):
    now_state = await state.get_state()
    if now_state == Profile.show_exercise:
        await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id - 1)
        await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
        await state.clear()
    student = await Students.get(tg_id=callback.from_user.id)
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
    keyboard = await student_confirm_task_kb(student)
    await state.set_state(Profile.student_confirm)
    try:
        await callback.message.edit_text(text=tasks_message, parse_mode="HTML", reply_markup=keyboard)
    except TelegramBadRequest:
        await callback.message.answer(text=tasks_message, parse_mode="HTML", reply_markup=keyboard)


@profile_router.callback_query(Text(text="student_confirm"), Profile.show_exercise)
async def student_confirm(callback: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    confirm_task_id = data['confirm_task_id']
    print(confirm_task_id)

    task: Tasks = await Tasks.get(id=confirm_task_id)
    await task.update(student_status=True, date_update_student=str(datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")))
    await callback.answer("Задача подтверждена!", show_alert=True)
    await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id - 1)
    await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
    await state.clear()


@profile_router.callback_query(Text(text="confirm_delete"))
async def confirm_delete_account(callback: CallbackQuery, state: FSMContext):
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





