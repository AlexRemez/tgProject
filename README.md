## Billiard_helper / Telegram_bot

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)

[@PoolBilliard_bot](https://t.me/PoolBilliard_bot)

<img src="images/bot_2.jpg" width="200" height="200" />

Асинхронный бот для облегчения взаимоотношения между тренером и учеником

Написан с использованием:
* aiogram 3.x
* telegram bot api
* asyncio
* SQLAlchemy
* asyncpg
* psycopg2
* pydantic
* alembic
* aiohttp

<img src="images/about.png" width="500" />



### Для работы необходимо указать следующие переменные окружения

    BOT_TOKEN = example_token
    
    # for database    
    DB_PARAMS = {'user': 'EXAMPLE', 'password': 'EXAMPLE', 'host': '127.0.0.1', 'database': 'tgBot'}

## Старт

Запуск бота:
```shell
python bot.py
