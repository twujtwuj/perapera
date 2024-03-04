# pydantic model
# validates request from react application
# based on validity, accepts or rejects into FastAPI application

from pydantic import BaseModel
from datetime import datetime


class Card(BaseModel):
    kanji: str
    strokes: int
    grade: int
    freq: int
    jlpt_new: int
    meanings: str
    readings_on: str
    readings_kun: str
    prev_review: datetime
    next_review: datetime
    seen: bool

# FRONT END
class CardModel(Card):
    id: int

    class Config:
        orm_mode = True


# from typing import List, Optional
# from datetime import datetime

#     meanings: Optional[List[str]]
#     readings_on: Optional[List[str]]
#     readings_kun: Optional[List[str]]
#     prev_review: Optional[datetime]
#     next_review: Optional[datetime]
