import asyncio
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from config_reader import config

from handlers import start_bot, exercises, add_exercises
import asyncpg

# параметры подключения к базе данных
db_params = config.db_params.get_secret_value()


# асинхронная функция для подключения к базе данных
async def connect_to_db():
    conn = await asyncpg.connect(**db_params)
    return conn


# # пример использования
# async def query_example():
#     conn = await connect_to_db()
#     # выполнение SQL-запроса
#     result = await conn.fetch('SELECT * FROM your_table')
#     await conn.close()
#     return result


def add_routes(dispatcher: Dispatcher):
    dispatcher.include_router(exercises.router_1)
    dispatcher.include_router(start_bot.router_2)
    dispatcher.include_router(add_exercises.router_3)


# Запуск процесса поллинга новых апдейтов
async def main():
    # Включаем логирование, чтобы не пропустить важные сообщения
    logging.basicConfig(level=logging.INFO)
    # Объект бота
    bot = Bot(token=config.bot_token.get_secret_value())
    # Диспетчер
    dp = Dispatcher()
    add_routes(dp)

    # await connect_to_db()

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
