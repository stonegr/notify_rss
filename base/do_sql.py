from common.models.url_data import UrlDatum

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from base.base import *

engine = create_engine("sqlite:///" + resource_path("static/db/rss.db"), echo=False)
Session = sessionmaker(bind=engine)

session = Session()

cs = session.query(UrlDatum).first()
print(cs.name)
print(cs.current_contents)
session.close()

cs = session.query(UrlDatum).first()
print(cs.name)
print(cs.current_contents)
