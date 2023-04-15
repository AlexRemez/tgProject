from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from config_reader import config

# параметры подключения к базе данных
db_params = eval(config.db_params.get_secret_value())


class Base(DeclarativeBase):
    pass


class AsyncDatabaseSession:
    def __init__(self):

        user = db_params['user']
        password = db_params['password']
        database = db_params["database"]
        host = db_params["host"]

        self._engine = create_async_engine(
            f'postgresql+asyncpg://{user}:{password}@{host}:5432/{database}',
            # echo=True,  # TODO: DB echo=True
        )
        self._session = async_sessionmaker(
            self._engine,
            expire_on_commit=False,
            class_=AsyncSession,
        )

    def __call__(self):
        return self._session()

    def __getattr__(self, name):
        return getattr(self._session, name)


async_db_session = AsyncDatabaseSession()
