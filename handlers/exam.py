from aiogram import Router, Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Text
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, FSInputFile
from sqlalchemy.exc import MultipleResultsFound

from db.models import Students, Coaches, Exercises, Tags, Athletes, ExerciseResults, ExerciseTag
from filters.filters_exam import is_better
from functions.exam_functions import calculate_points
from handlers.authorization import Auth
from keyboards.for_exam import exam_alert_kb, exam_ex_level_kb, exam_ex_num_kb, exam_choose_confirm, exam_notify, \
    exam_access_kb, my_exam_kb, exam_preparation_kb, start_exam_kb, exam_attempt_kb, finish_exam_kb
from keyboards.for_start_bot import back_menu_kb

exam_router = Router()


@exam_router.callback_query(Text(text="exam"))
async def exam_alert(callback: CallbackQuery, state: FSMContext):
    student = await Students.get(tg_id=callback.from_user.id)
    if student:
        await state.update_data(student_exam=student)

    text = "<b>А ВЫ ГОТОВЫ К БОЮ НА СТОЛЕ БИЛЬЯРДНОГО ЗАЛА⁉️</b>\
    \n\n<i>Если да, то добро пожаловать на экзамен по бильярду❗️ " \
           "Здесь нет места для слабаков и трусов - только самые смелые и " \
           "опытные игроки могут справиться с этим вызовом.</i>"
    await callback.message.edit_text(
        text=text,
        reply_markup=exam_alert_kb()
    )


@exam_router.callback_query(Text("exam_choose_ex"))
async def exam_ex_filter(callback: CallbackQuery, state: FSMContext):
    await state.update_data(flag=False)
    athlete = await Athletes.get(tg_id=callback.from_user.id)

    if athlete is None:
        await state.set_state(Auth.athlete_first_name)
        await callback.answer(text="Нам нужны некоторые данные для регистрации "
                                   "в таблице лидеров и связи с вами😜",
                              show_alert=True)
        await callback.message.edit_text(
            text="<b>Введите своё имя</b>"
                 "\n\n<u>Пожалуйста вводите действительную информацию, ваши данные будут проверены!</u>",
            reply_markup=back_menu_kb(text="Отмена")
        )

    elif not athlete.is_active:
        await callback.answer(text="Ожидайте подтверждения вашей заявки⏳", show_alert=True)
    else:
        text = "<b>ЭТАП 1: ВЫБОР УПРАЖНЕНИЯ.</b> \n\n<i>Мы знаем, что вы хотите выбрать самое сложное упражнение, " \
           "чтобы показать всем свои навыки. Идите на все или ничего, ребята❗️ " \
           "Выбирайте упражнение по уровню своих навыков или по сложности - главное, " \
           "не забывайте, что только сильнейшие могут выжить на этом экзамене❗️</i>"

        keyboard = exam_ex_level_kb()

        await callback.message.edit_text(text=text, reply_markup=keyboard)


@exam_router.callback_query(Text(startswith="level"))
async def level_exercise(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    flag = data['flag']

    level = callback.data
    await state.update_data(level=level)

    print(level)
    tag: Tags = await Tags.get(tag_name=level)
    exercises = await tag.get_exercises()
    print(f"Список упражнений для тега {tag.tag_name}: {exercises}")

    text = "<i><b>Слушай, мачо🤠</b> " \
           "\nТы готов выбрать номер своего упражнения❓ " \
           "Здесь нет места для трусов и нерешительных💯 Приготовься к бомбардировке своих навыков❗️ " \
           "\nСкажи мне, на какой номер ты ставишь❓ Будешь смелым и выберешь самое жесткое упражнение " \
           "или предпочтешь осторожно потоптаться на безопасной зоне😱 Номер - это твой выбор, " \
           "и он будет определять, кто ты здесь и с чем идешь на бильярдную арену🏆 " \
           "\nТак что, дерзай, герой🦸 Назови свой номер и покажи всем, " \
           "что ты - настоящий босс бильярдного стола😎</i>"

    keyboard = exam_ex_num_kb(exercises)

    if flag:
        await callback.message.delete()
        await callback.message.answer(text=text, reply_markup=keyboard)
    else:
        await callback.message.edit_text(text=text, reply_markup=keyboard)


@exam_router.callback_query(Text(startswith="exam_ex_num"))
async def exam_show_ex(callback: CallbackQuery, state: FSMContext):
    await state.update_data(flag=True)
    await callback.message.delete()

    data = callback.data.split("-")
    exercise: Exercises = await Exercises.get(id=int(data[1]))

    await state.update_data(exam_ex=exercise)

    img = FSInputFile("images/" + exercise.path)
    if exercise.description:
        description = f'\n{exercise.description}'
    else:
        description = ''
    if exercise.rules:
        rules = f'\nПравила выполнения:\n{exercise.rules}'
    else:
        rules = ''

    athlete_tg_id = callback.from_user.id
    athlete = await Athletes.get(tg_id=athlete_tg_id)

    exam = await ExerciseResults.get(athlete_id=athlete.id,
                                     exam_status=True,
                                     exercise_id=exercise.id,
                                     completed_status=True)
    if exam:
        best_result = f"\n\n<b>Ваш лучший результат:</b>" \
                      f"\n{exam.results}"
    else:
        best_result = ""

    data = await state.get_data()
    level = data['level']
    keyboard = exam_choose_confirm(level=level)

    await callback.message.answer_photo(
        img,
        caption=f'<b>Упражнение {exercise.id}:</b><i>{description}</i>{rules}{best_result}',
        reply_markup=keyboard
    )


@exam_router.callback_query(Text("exam_choose_ex_confirm"))
async def notify_org(callback: CallbackQuery, state: FSMContext, bot: Bot):

    # Готовим данные для уведомлений
    data = await state.get_data()
    athlete_tg_id = callback.from_user.id
    exercise = data['exam_ex']
    athlete = await Athletes.get(tg_id=athlete_tg_id)

    if await ExerciseResults.get(athlete_id=athlete.id,
                                 exam_status=True,
                                 exercise_id=exercise.id,
                                 completed_status=False):
        await callback.answer(text=f"Вы уже подали заявку на это упражнение☑️", show_alert=True)
    elif await ExerciseResults.get(athlete_id=athlete.id, exam_status=True, completed_status=False):
        await callback.answer(text=f"Вы уже подали заявку на другое упражнение☑️", show_alert=True)
    else:
        await callback.message.delete()
        text = "<i>Слушай, тигр🐅 Ты отправил заявку на проведение этого экзамена. " \
               "Настало время ожидания⏳ Это как сидеть на растерзание акулам, " \
               "правда?🦈 Но не беспокойся, герой, ты сделал свое дело, а судьба теперь в руках бильярдных богов💫</i>"

        await callback.message.answer(
            text=text
        )

        username = str(callback.from_user.username)
        if username == "None":
            username = "Неизвестно"
        else:
            username = "@" + username

        athlete_first_name = athlete.first_name
        athlete_last_name = athlete.last_name
        athlete_email = athlete.email

        ################################################################
        flag = True
        try:
            student: Students = data["student_exam"]
        except KeyError:
            flag = False

        flag_2 = True
        if flag:
            coach: Coaches = await Coaches.get(id=student.coach_id)
            if coach is None:
                flag = False
            else:
                if coach.tg_id == 5691938305:
                    flag_2 = False

        await ExerciseResults.create(
            exam_status=True,
            athlete_id=athlete.id,
            exercise_id=exercise.id
        )

        exam = await ExerciseResults.get(athlete_id=athlete.id,
                                         exam_status=True,
                                         exercise_id=exercise.id,
                                         completed_status=False)

        ################################################################
        # Отправляем уведомление ответственному за экзамен человеку (не тренер)
        if flag_2:

            text = f"💬<b>Запрос на экзамен</b>💬"\
                   f"\n<b>Имя:</b> {athlete_first_name}"\
                   f"\n<b>Фамилия:</b> {athlete_last_name}"\
                   f"\n<b>Упражнение:</b> №{exercise.id}"\
                   f"\n\n<b>Username:</b> {username}"\
                   f"\n<b>Почта:</b> {athlete_email}"

            await bot.send_message(chat_id=5691938305,
                                   text=text,
                                   reply_markup=exam_notify(exam.id))

        # Если ученик, то отправляем уведомление еще и его тренеру
        if flag:
            text = f"💬<b>Запрос на экзамен</b>💬"\
                   f"\n<b>Ваш ученик:</b> {athlete_first_name} {athlete_last_name}" \
                   f"\n<b>Упражнение:</b> №{exercise.id}"\
                   f"\n\n<b>Username:</b> {username}"

            if not flag_2:
                text += f"\n<b>Почта:</b> {athlete_email}"

            await bot.send_message(
                chat_id=coach.tg_id,
                text=text,
                reply_markup=exam_notify(exam_id=exam.id)
            )


@exam_router.callback_query(Text(startswith="check_exam"))
async def check_exam(callback: CallbackQuery):
    exam_id = callback.data.split("-")[1]
    try:
        if callback.data.split("-")[2]:
            continue_exam = True
        print("Получил уведомление о проведении экзамена")
    except IndexError:
        continue_exam = False
        print(f"Просматривает упражнение №{exam_id}")
    exam = await ExerciseResults.get(id=int(exam_id))
    print(exam.exam_status, exam.exercise.id, exam.athlete.first_name)

    img = FSInputFile("images/" + exam.exercise.path)
    if exam.exercise.description:
        description = f'\n{exam.exercise.description}'
    else:
        description = ''
    if exam.exercise.rules:
        rules = f'\nПравила выполнения:\n{exam.exercise.rules}'
    else:
        rules = ''

    tags = exam.exercise.tags
    print(tags)
    ex_tags = "\n\n"
    for tag in tags:
        tag: ExerciseTag
        ex_tags += f"{tag.tag.tag_name} "
    if callback.from_user.id == 5691938305 and not continue_exam:
        await callback.message.delete()
        keyboard = exam_access_kb(exam_id)
    elif callback.from_user.id == exam.athlete.tg_id:
        await callback.message.delete()
        keyboard = exam_preparation_kb(exam_id)
    else:
        keyboard = None
    print(ex_tags)

    await callback.message.answer_photo(img,
                                        caption=f'<b>Упражнение {exam.exercise.id}:</b><i>{description}</i>{rules}'
                                                f'{ex_tags}',
                                        reply_markup=keyboard)


@exam_router.callback_query(Text(startswith="exam_access"))
async def exam_access(callback: CallbackQuery, bot: Bot):
    exam_id = callback.data.split("-")[1]
    exam = await ExerciseResults.get(id=int(exam_id))

    await callback.message.delete()
    await callback.message.answer(
        text=f"<b>{exam.athlete.first_name} {exam.athlete.last_name} допущен к экзамену✅</b>"
    )

    keyboard = my_exam_kb(exam_id, continue_exam=True)
    await bot.send_message(
        chat_id=exam.athlete.tg_id,
        text="<b>Вы допущены к экзамену✅</b>",
        reply_markup=keyboard
    )


@exam_router.callback_query(Text(startswith="exam_forbid"))
async def exam_forbid(callback: CallbackQuery, bot: Bot):
    exam_id = callback.data.split("-")[1]
    exam = await ExerciseResults.get(id=int(exam_id))
    athlete_tg_id = exam.athlete.tg_id

    await exam.delete()
    await callback.message.delete()
    await callback.message.answer(text="<b>В проведении экзамена отклонено❌</b>")

    await bot.send_message(
        chat_id=athlete_tg_id,
        text="<b>Ваш запрос на экзамен отклонён❌</b>"
    )


@exam_router.callback_query(Text(text="hide_message"))
async def hide_message(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(
        text="<b>Экзамен отложен✖️</b>"
    )


@exam_router.callback_query(Text(startswith="preparation_cam"))
async def preparation_cam(callback: CallbackQuery):
    exam_id = callback.data.split("-")[1]

    text = "<b>Подготовься к съемке, герой!</b> \n<i>Заряди камеру бесстрашием, " \
           "найди потрясающий ракурс и поставь на столе упражнение, " \
           "которое покажет, кто здесь настоящий король бильярда. " \
           "Это твой момент, и ты готов сделать его великим!</i>" \
           "\n\nP.S. <u>Всё должно быть снято одним дублем.</u>"

    keyboard = start_exam_kb(exam_id)

    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(
        text=text,
        reply_markup=keyboard
    )


@exam_router.callback_query(Text(startswith="start_exam"))
async def exam_attempt(callback: CallbackQuery, state: FSMContext):
    data = callback.data.split("-")
    exam_id = data[1]
    print(callback.data)

    try:
        result = data[3]
    except IndexError:
        await state.update_data(results_list=[])
        result = None

    if result == "good":
        state_data = await state.get_data()
        results_list = state_data['results_list']
        results_list.append(True)
        await state.update_data(results_list=results_list)
        print(results_list)
    elif result == "bad":
        state_data = await state.get_data()
        results_list = state_data['results_list']
        results_list.append(False)
        await state.update_data(results_list=results_list)
        print(results_list)

    try:
        attempt = int(data[2]) + 1
    except IndexError:
        attempt = 1

    if attempt <= 10:
        keyboard = exam_attempt_kb(exam_id, attempt)
        await callback.message.edit_text(
            text=f"<b>{attempt} ПОДХОД</b>",
            reply_markup=keyboard
        )
    else:
        state_data = await state.get_data()
        results_list = state_data['results_list']
        text_result = ""
        for result in results_list:
            if result:
                text_result += "✅"
            else:
                text_result += "❌"

        athlete = await Athletes.get(tg_id=callback.from_user.id)
        exam = await ExerciseResults.get(id=int(exam_id))

        best_exam = await ExerciseResults.get(athlete_id=athlete.id,
                                              exam_status=True,
                                              exercise_id=exam.exercise_id,
                                              completed_status=True)
        if best_exam:
            if is_better(best_exam, text_result):
                await exam.update(results=text_result)
                points = await calculate_points(exam.id)
                previous_score = athlete.points
                new_score = (previous_score - best_exam.points) + points
                await best_exam.update(results=text_result, points=points)
                await athlete.update(points=new_score)
                await callback.message.edit_text(
                    text=f"<b>Ваш результат обновлён:</b>"
                         f"\n\n<b>Ваш лучший результат:</b>"
                         f"\n{best_exam.results}"
                         f"\n\n<b>Текущий результат:</b>"
                         f"\n{text_result}"
                         f"\n\n<b>Рейтинговые очки обновлены:</b>"
                         f"\n<i>{previous_score}</i> ➡️ <b>{new_score}</b>"
                )
            else:
                await callback.message.edit_text(
                    text=f"<b>УВЫ❗️</b>"
                         f"\n\n<b>Ваш лучший результат:</b>"
                         f"\n{best_exam.results}"
                         f"\n\n<b>Текущий результат:</b>"
                         f"\n{text_result}"
                )
            await exam.delete()
        else:
            await exam.update(results=text_result, completed_status=True)
            points = await calculate_points(exam.id)
            await exam.update(points=points)
            previous_score = athlete.points
            new_score = previous_score + points
            await athlete.update(points=new_score)
            await callback.message.edit_text(
                text=f"<b>Ваш результат сохранён:</b>"
                     f"\n{text_result}"
                     f"\n\n<b>Рейтинговые очки обновлены:</b>"
                     f"\n<i>{previous_score}</i> ➡️ <b>{new_score}</b>"
            )
