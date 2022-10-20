# coding: utf-8
from sqlalchemy import Column, DateTime, Integer, String, text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class UserLog(Base):
    __tablename__ = 'user_log'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    current_contents = Column(String)
    last_update = Column(DateTime, nullable=False, server_default=text("datetime('now','localtime')"))
