from aiogram import Router, types, Bot
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from keyboards.for_start_bot import main_buttons_kb

router_2 = Router()


def make_start_message(query):
    if isinstance(query, Message):
        name = query.from_user.first_name
    elif isinstance(query, CallbackQuery):
        name = query.from_user.first_name

    start_message = f"""<b>Привет, {name}!</b>
    <i>Я бот, готовый помочь Вам с тренировочным процессом.</i>
    
    Чтобы увидеть список команд нажмите кнопку "Меню" слева от поля ввода!
    
    Если у Вас есть вопросы, пожалуйста, напишите мне @prog_Alkis!
    """
    return start_message


# Хэндлер на команду /start
@router_2.message(Command("start"))
async def cmd_start(message: Message, bot: Bot):
    print(message.from_user)
    try:
        await message.delete()
    except TypeError:
        print("start message error")
    await message.answer(make_start_message(message), parse_mode="HTML", reply_markup=main_buttons_kb())
