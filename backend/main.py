from fastapi import FastAPI, Depends, HTTPException
import schemas as schemas
import models as models
from data_loader import data_loader
import pandas as pd
from datetime import datetime, timedelta
from database import Base, engine, SessionLocal
from sqlalchemy.orm import Session
#from apscheduler.schedulers.background import BackgroundScheduler

# FRONT END --------
from fastapi.middleware.cors import CORSMiddleware  # Enable cors for dealing with cross-origin communication
# ------------------

Base.metadata.create_all(engine)  # sets up SQLite data base


def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


app = FastAPI()

# CORS FOR FRONT END -----------------
origins=  [
    "http://localhost:3000", 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)
# -----------------------------------

INTERVAL_SCALER = {1: 0, 2: 1, 3: 1.5, 4: 2}
NEXT_CARD_ID = None

# New card limit / review limit / deal with no new cards left
TODAYS_REVIEWS = 0
MAX_REVIEWS = 2


# # Reset function
# def reset_todays_reviews():
#     global TODAYS_REVIEWS
#     TODAYS_REVIEWS = 0
#     print("Card reviews reset to 0.")
# # Background task to reset reviews
# def reset_reviews(background_tasks: BackgroundTasks):
#     background_tasks.add_task(reset_todays_reviews)


# Load the data base when app is started
@app.on_event("startup")
async def startup_event(): #background_tasks: BackgroundTasks): #background_tasks: BackgroundTasks):
   
    # Load data in from JSON
    with SessionLocal() as session:

        # Delete all records from the Card table
        session.query(models.Card).delete()

        kanji_df = data_loader()

        # Insert data into the database
        for _, row in kanji_df.iterrows():
            card = models.Card(**row)
            session.add(card)
            session.commit()
            session.refresh(card)

    # # Schedule card review limit to reset every day at midnight
    # midnight = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
    # time_until_midnight = (midnight - datetime.now()).total_seconds()
    # background_tasks.add_task(reset_reviews, background_tasks, delay=time_until_midnight)



# Get all cards
@app.get("/all_cards")
def getAllCards(session: Session = Depends(get_session)):
    cards = (
        session.query(models.Card)
        .order_by(models.Card.id.asc())
        .all()
    )
    return cards

# Get all seen cards, and order them by their review dates
@app.get("/seen_cards")
def getSeenCards(session: Session = Depends(get_session)):
    cards = (
        session.query(models.Card)
        .filter(models.Card.seen == True)
        .order_by(models.Card.next_review.asc())
        .all()
    )
    return cards


# # Get a card with ID
# @app.get("/get_card/{id}")
# def getCard(id: int, session: Session = Depends(get_session)):
#     card = session.query(models.Card).get(id)
#     return card


# Get a card that is due i.e. next_review is set to today, with lowest ID number
@app.get("/next_card")
def getNextCard(session: Session = Depends(get_session)):
    global NEXT_CARD_ID
    # global TODAYS_REVIEWS
    # global MAX_REVIEWS

    # # Check if review limit reached
    # if TODAYS_REVIEWS > MAX_REVIEWS:
    #     raise HTTPException(status_code=429, detail="Card review limit reached")
    # TODAYS_REVIEWS =+ 1
    
    card = (
        session.query(models.Card)
        .filter(models.Card.next_review <= datetime.now().date() + timedelta(days=1))
        .order_by(models.Card.id.asc())
        .first()
    )

    # Check if a card is found
    if not card:
        raise HTTPException(status_code=404, detail="No card found for review today")

    NEXT_CARD_ID = card.id

    return card


# Update the previous and next review dates for the current card
@app.put("/next_card_review")
def updateCardReview(rating: int, session: Session = Depends(get_session)):
    global NEXT_CARD_ID

    # Check if next card has been called
    if NEXT_CARD_ID is None:
        raise HTTPException(status_code=400, detail="Call /next_card before review")

    # Fetch the card by ID
    card = session.query(models.Card).get(NEXT_CARD_ID)

    # Check if the card exists
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    
    # Set card to seen
    card.seen = True

    # Check valid rating
    if rating not in [1, 2, 3, 4]:
        raise HTTPException(status_code=422, detail="Rating must be between 1 and 4")

    # Update review dates based on rating
    current_interval = card.next_review - card.prev_review + timedelta(days=1)
    current_date = datetime.now().date()
    rounded_days = round(
        current_interval.total_seconds() / (24 * 60 * 60) * INTERVAL_SCALER[rating]
    )
    rounded_interval = timedelta(days=rounded_days)
    card.prev_review = current_date
    card.next_review = current_date + rounded_interval + timedelta(days=1)

    session.commit()

    return f"Next review for card {NEXT_CARD_ID} in {rounded_interval} days ({rating})"


# Add a new card, automatically set to review tomorrow
@app.post("/new_card")
def addCard(card: schemas.Card, session: Session = Depends(get_session)):
    card = models.Card(
        prev_review=datetime.now().date(),
        next_review=datetime.now().date() + timedelta(days=1),
        kanji=card.kanji,
        strokes=card.strokes,
        grade=card.grade,
        freq=card.freq,
        jlpt_new=card.jlpt_new,
        meanings=card.meanings,
        readings_on=card.readings_on,
        readings_kun=card.readings_kun,
    )
    session.add(card)
    session.commit()
    session.refresh(card)
    return card

# Delete card by ID
@app.delete("/delete/{id}")
def delete_card_by_id(id: int, session: Session = Depends(get_session)):
    card = session.query(models.Card).get(id)
    if card:
        session.delete(card)
        session.commit()
        session.close()
        return f"Card {id} with kanji {card.kanji} was deleted"
    else:
        raise HTTPException(status_code=404, detail=f"Card with ID {id} not found")

# # Delete card by kanji
# @app.delete("/delete/{kanji}")
# def delete_card_by_kanji(kanji: str, session: Session = Depends(get_session)):
#     card = (
#         session.query(models.Card)
#         .filter(models.Card.kanji == kanji)
#         .first()
#     )
#     if card:
#         session.delete(card)
#         session.commit()
#         session.close()
#         return f"Card {card.id} with kanji {card.kanji} was deleted"
#     else:
#         raise HTTPException(status_code=404, detail=f"Card with kanji {kanji} not found")
