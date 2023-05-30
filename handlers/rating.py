from aiogram import Router, Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Text
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, FSInputFile

from db.models import Athletes, ExerciseResults
from keyboards.for_profile import back

rating_router = Router()


@rating_router.callback_query(Text(text="exam_rating"))
async def exam_rating(callback: CallbackQuery):
    athletes_list = await Athletes.sort(Athletes.points, method="-")

    text = "⠀⠀⠀⠀⠀⠀⠀<b>📃РЕЙТИНГ📃</b>"

    for athlete in athletes_list:
        athlete: Athletes
        exercises: ExerciseResults = await ExerciseResults.filter(athlete_id=athlete.id,
                                                                  exam_status=True,
                                                                  completed_status=True)
        count_exercises = len(exercises)
        text += f"\n<b>{athlete.first_name} {athlete.last_name}</b> | {count_exercises} упр. | {athlete.points} очков"

    await callback.message.edit_text(text=text,
                                     reply_markup=back("main_menu"))
