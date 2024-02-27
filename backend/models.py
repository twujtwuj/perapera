# SQLite tables

from sqlalchemy import Column, Integer, String, DateTime, Boolean
from database import Base


class Card(Base):
    __tablename__ = "cards"

    id = Column(Integer, primary_key=True, index=True)
    kanji = Column(String, index=True)
    strokes = Column(Integer)
    grade = Column(Integer)
    freq = Column(Integer, index=True)
    jlpt_new = Column(Integer)
    meanings = Column(String)
    readings_on = Column(String)
    readings_kun = Column(String)
    prev_review = Column(DateTime)
    next_review = Column(DateTime)
    seen = Column(Boolean)
