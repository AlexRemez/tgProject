from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

router_2 = Router()


def make_start_message(query):
    if isinstance(query, Message):
        name = query.from_user.first_name
    elif isinstance(query, CallbackQuery):
        name = query.from_user.first_name

    start_message = f"""<b>Привет, {name}!</b>
    <i>Я бот, готовый помочь Вам в выполнении задач.</i>
    
    Список моих команд:
    /start - Начать работу с ботом
    
    /list_drills - Выбрать упражнение
    /show_all_drills - Все упражнения
    /add_exercise - Добавить свое упражнение
    
    Если у Вас есть вопросы, пожалуйста, напишите мне @prog_Alkis!
    """
    return start_message


# Хэндлер на команду /start
@router_2.message(Command("start"))
async def cmd_start(message: Message):
    print(message.from_user)

    await message.answer(make_start_message(message), parse_mode="HTML")
