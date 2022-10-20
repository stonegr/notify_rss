# coding: utf-8
from sqlalchemy import Column, Date, DateTime, Index, Integer, String, text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class UrlDatum(Base):
    __tablename__ = 'url_data'
    __table_args__ = (
        Index('url_data_name_date', 'name', 'date', unique=True),
    )

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    current_contents = Column(String)
    current0_today = Column(String)
    today_contents = Column(String)
    need_update = Column(Integer, nullable=False, index=True, server_default=text("1"))
    date = Column(Date, nullable=False, server_default=text("date('now','localtime')"))
    last_update = Column(DateTime, nullable=False, server_default=text("datetime('now','localtime')"))
    enable = Column(Integer, nullable=False, server_default=text("1"))
