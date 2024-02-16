from fastapi import FastAPI, Depends, HTTPException #BackgroundTasks
import schemas
import models
import pandas as pd
from datetime import datetime, timedelta
from database import Base, engine, SessionLocal
from sqlalchemy.orm import Session

Base.metadata.create_all(engine)  # sets up SQLite data base


def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


app = FastAPI()

INTERVAL_SCALER = {1: 0, 2: 1, 3: 1.5, 4: 2}
NEXT_CARD_ID = None
#CARD_REVIEW_LIMIT = 2
# CARDS_REVIEWED = 0


# def reset_card_reviews():
#     global CARD_REVIEWS
#     CARD_REVIEWS = 0
#     print("Card reviews reset to 0.")


# Load the data from JSON
def load_data():
    with SessionLocal() as session:
        # Read JSON file with Pandas
        kanji_df = pd.read_json("kanji-kyouiku.json", orient="index")[:4]
        kanji_df.reset_index(inplace=True)
        kanji_df.rename(columns={"index": "kanji"}, inplace=True)
        cols = [
            "kanji",
            "strokes",
            "grade",
            "freq",
            "jlpt_new",
            "meanings",
            "readings_on",
            "readings_kun",
        ]
        kanji_df = kanji_df[cols]

        # Select the first element of the lists for meanings, readings_on, and readings_kun
        kanji_df["meanings"] = kanji_df["meanings"].apply(lambda x: x[0] if x else None)
        kanji_df["readings_on"] = kanji_df["readings_on"].apply(
            lambda x: x[0] if x else None
        )
        kanji_df["readings_kun"] = kanji_df["readings_kun"].apply(
            lambda x: x[0] if x else None
        )

        # 'Reset' the review
        kanji_df["prev_review"] = datetime.now().date()
        kanji_df["next_review"] = datetime.now().date()

        # Convert 'freq' column to integer
        kanji_df["freq"] = (
            pd.to_numeric(kanji_df["freq"], errors="coerce").fillna(0).astype(int)
        )

        # Insert data into the database
        for _, row in kanji_df.iterrows():
            card = models.Card(**row)
            session.add(card)
            session.commit()
            session.refresh(card)


# Load the data base when app is started
@app.on_event("startup")
async def startup_event(): #background_tasks: BackgroundTasks):
    # Load data in from JSON
    load_data()

    # # Schedule card review limit to reset every midnight
    # midnight = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    # time_until_midnight = (midnight - datetime.now()).total_seconds()
    # background_tasks.add_task(reset_card_reviews, delay=time_until_midnight)


# Get all cards
@app.get("/")
def getCards(session: Session = Depends(get_session)):
    cards = session.query(models.Card).all()
    return cards


# Get a card with ID
@app.get("/get_card/{id}")
def getCard(id: int, session: Session = Depends(get_session)):
    card = session.query(models.Card).get(id)
    return card


# Get a card that is due i.e. next_review is set to today, with lowest ID number
@app.get("/next_card")
def getNextCard(session: Session = Depends(get_session)):
    global NEXT_CARD_ID
    # global CARD_REVIEW_LIMIT
    # global CARDS_REVIEWED

    # Check if review limit reached
    # if CARDS_REVIEWED > CARD_REVIEW_LIMIT:
    #     raise HTTPException(status_code=429, detail="Card review limit reached")
    # CARDS_REVIEWED =+ 1
    
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
    card.next_review = current_date + timedelta(days=1) + rounded_interval

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


# Delete cards
@app.delete("/{id}")
def deleteCard(id: int, session: Session = Depends(get_session)):
    card = session.query(models.Card).get(id)
    session.delete(card)
    session.commit()
    session.close()
    return "Card {id} was deleted"
