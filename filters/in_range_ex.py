from aiogram.filters import BaseFilter
from aiogram.types import CallbackQuery, Message

from db.models import Exercises


class ValidExerciseFilter(BaseFilter):

    async def __call__(self, message: Message) -> bool:
        text = message.text
        print(text)
        if text.isdigit():
            print("digit")
            ex = await Exercises.get(id=int(text))
            if ex:
                return True
        print("bad")
        return False


