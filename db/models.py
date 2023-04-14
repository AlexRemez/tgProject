from sqlalchemy import create_engine, Column, Integer, String, MetaData
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Exercises(Base):
    __tablename__ = 'exercises'

    id = Column(Integer, primary_key=True)
    ex_num = Column(Integer)
    name = Column(String)
    path = Column(String)
    description = Column(String)
    rules = Column(String)


