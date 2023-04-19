from aiogram.filters import BaseFilter
from aiogram.types import Message

from db.models import Coaches, Students


class IsAuth(BaseFilter):

    async def __call__(self, message: Message) -> bool:
        user_id = message.from_user.id
        coach = await Coaches.get(tg_id=user_id)
        student = await Students.get(tg_id=user_id)
        if coach or student:
            return True
        else:
            return False
