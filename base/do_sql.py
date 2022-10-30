from common.models.url_data import UrlDatum

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

from base.base import *
from common.config_do import Config_do

# engine = create_engine(
#     "sqlite:////" + resource_path("static/database/rss.db"), echo=False
# )
_db_path = Config_do.get_self(
    Config_do.config, ["config", "db_file"], "static/database/rss.db"
)
# print(_db_path)
engine = create_engine("sqlite:///" + os.path.abspath(_db_path), echo=False)
# engine = create_engine("sqlite:///static/database/rss.db", echo=False)
Session = sessionmaker(bind=engine)

session = Session()

# cs = session.query(UrlDatum).first()
# print(cs.name)
# print(cs.current_contents)
# session.close()

# cs = session.query(UrlDatum).first()
# print(cs.name)
# print(cs.current_contents)
