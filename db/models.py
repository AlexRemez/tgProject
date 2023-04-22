import datetime

from sqlalchemy import Column, Integer, String, Boolean, BigInteger, exc, func, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import load_only, relationship, backref

from .connect import async_db_session
from sqlalchemy.sql import select, insert, update


Base = declarative_base()


class ModelAdmin:
    @classmethod
    async def create(cls, **kwargs) -> None:
        """
        # Создаем новый объект
        :param kwargs: Поля и значения для объекта
        :return: Идентификатор PK
        """

        async with async_db_session() as session:
            await session.execute(insert(cls).values(**kwargs))
            await session.commit()

    @classmethod
    async def add(cls, **kwargs) -> None:
        """
        # Добавляем новый объект
        :param kwargs: Поля и значения для объекта
        """

        async with async_db_session() as session:
            await session.add(cls(**kwargs))
            await session.commit()

    async def update(self, **kwargs) -> None:
        """
        # Обновляем текущий объект
        :param kwargs: поля и значения, которые надо поменять
        """

        async with async_db_session() as session:
            cls = type(self)
            update_stmt = (
                update(cls)
                .where(cls.id == self.id)
                .values(**kwargs)
            )
            await session.execute(update_stmt)
            await session.commit()

    async def delete(self) -> None:
        """
        # Удаляем объект
        """
        async with async_db_session() as session:
            await session.delete(self)
            await session.commit()

    @classmethod
    async def get(cls, **kwargs):
        """
        # Возвращаем одну запись, которая удовлетворяет введенным параметрам
        :param kwargs: поля и значения
        :return: Объект или None
        """

        params = [getattr(cls, key) == val for key, val in kwargs.items()]
        query = select(cls).where(*params)
        try:
            async with async_db_session() as session:
                results = await session.execute(query)
                (result,) = results.one()
                result: cls
                return result
        except exc.NoResultFound:
            return None

    @classmethod
    async def filter(cls, **kwargs):
        """
        # Возвращаем все записи, которые удовлетворяют фильтру
        :param kwargs: поля и значения
        :return: ScalarResult, если нашли записи и пустой tuple, если нет
        """

        params = [getattr(cls, key) == val for key, val in kwargs.items()]
        query = select(cls).where(*params)
        try:
            async with async_db_session() as session:
                results = await session.execute(query)
                res = results.scalars()
                return res.fetchall()
        except exc.NoResultFound:
            return ()

    @classmethod
    async def all(cls, values=None):
        """
        # Получаем все записи
        :param values: Список полей, которые надо вернуть, если нет, то все (default None)
        :return: ScalarResult записей
        """

        if values and isinstance(values, list):
            # Определенные поля
            values = [getattr(cls, val) for val in values if isinstance(val, str)]
            query = select(cls).options(load_only(*values))
        else:
            # Все поля
            query = select(cls)

        async with async_db_session() as session:
            result = await session.execute(query)
            res = result.scalars()
            return res.fetchall()

    @classmethod
    async def max_id(cls):
        try:
            async with async_db_session() as session:
                result = await session.execute(func.max(cls.id))
                return result.scalar()
        except exc.NoResultFound:
            return ()


class Exercises(Base, ModelAdmin):
    __tablename__ = 'exercises'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    path = Column(String)
    description = Column(String)
    rules = Column(String)

    exercises = relationship("Tasks", back_populates="exercise")


class Coaches(Base, ModelAdmin):
    __tablename__ = 'coaches'

    id = Column(Integer, primary_key=True, autoincrement=True)
    tg_id = Column(BigInteger, nullable=False)
    first_name = Column(String(length=30))
    username = Column(String(length=30))
    telephone = Column(String(length=20))
    date_auth = Column(String, default=str(datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")))

    students = relationship("Students", back_populates="coach")


class Students(Base, ModelAdmin):
    __tablename__ = 'students'

    id = Column(Integer, primary_key=True, autoincrement=True)
    tg_id = Column(BigInteger, nullable=False)
    first_name = Column(String(length=30))
    username = Column(String(length=30))
    telephone = Column(String(length=20))
    date_auth = Column(String, default=str(datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")))

    coach_id = Column(Integer, ForeignKey("coaches.id"))
    coach = relationship("Coaches", back_populates="students", lazy=False)

    tasks = relationship("Tasks", back_populates="student", cascade="all, delete")


class Tasks(Base, ModelAdmin):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True, autoincrement=True)
    date_registered = Column(String, default=str(datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")))
    student_status = Column(Boolean, default=False)
    date_update_student = Column(String)

    coach_status = Column(Boolean, default=False)
    date_update_coach = Column(String)

    exercise_id = Column(Integer, ForeignKey("exercises.id"))
    exercise = relationship("Exercises", back_populates="exercises")

    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"))
    student = relationship("Students", back_populates="tasks")



    
