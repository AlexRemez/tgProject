import datetime

from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Exercises(Base):
    __tablename__ = 'exercises'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    path = Column(String)
    description = Column(String)
    rules = Column(String)


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, autoincrement=True)
    tg_id = Column(Integer, nullable=False)
    first_name = Column(String(length=30))
    username = Column(String(length=30))
    telephone = Column(String(length=20))
    is_coach = Column(Boolean)
    date_auth = Column(DateTime, default=datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S"))
