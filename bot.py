import asyncio
import logging
from aiogram import Bot, Dispatcher
from config_reader import config
from handlers import start_bot, exercises, add_exercises, authorization, profile, menu, exam, rating


def add_routes(dispatcher: Dispatcher):
    dispatcher.include_router(menu.menu_router)
    dispatcher.include_router(exercises.router_1)
    dispatcher.include_router(start_bot.router_2)
    dispatcher.include_router(add_exercises.router_3)
    dispatcher.include_router(authorization.auth_router)
    dispatcher.include_router(profile.profile_router)
    dispatcher.include_router(exam.exam_router)
    dispatcher.include_router(rating.rating_router)


# Запуск процесса поллинга новых апдейтов
async def main():
    # Включаем логирование, чтобы не пропустить важные сообщения
    logging.basicConfig(level=logging.INFO)
    # Объект бота
    bot = Bot(token=config.bot_token.get_secret_value(), parse_mode="HTML")
    # Диспетчер
    dp = Dispatcher()
    add_routes(dp)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
