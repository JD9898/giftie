import random
from fastapi import FastAPI, Query
from pydantic import BaseModel
from typing import List
from datetime import date
from typing import Dict
from sqlmodel import Field, Session, SQLModel, create_engine, select

app = FastAPI()

class FriendCreate(SQLModel):
    name: str
    birthday: date  # FastAPI will parse string → date here
class Friend(FriendCreate, table=True):
    id: int | None = Field(default=None, primary_key=True)

class GiftRequest(BaseModel):
    name: str
    # birthday: date
    sentiment: str  # e.g., "secret crush", "mentor"

class GiftHistory(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    recipient: str
    # birthday: date
    sentiment: str
    suggested_gift: str

sqlite_url = "sqlite:///./giftie.db"
engine = create_engine(sqlite_url, echo=True)

# Create the table on startup
SQLModel.metadata.create_all(engine)

@app.post("/api/gift-history")
def save_gift(gift: GiftHistory):
    with Session(engine) as session:
        session.add(gift)
        session.commit()
        session.refresh(gift)
    return {"message": "Gift saved", "gift": gift}


@app.get("/api/gift-history", response_model=list[GiftHistory])
def get_gift_history(recipient: str = Query(None)):
    with Session(engine) as session:
        statement = select(GiftHistory)
        if recipient:
            statement = statement.where(GiftHistory.recipient == recipient)
        results = session.exec(statement).all()
    return results


@app.post("/api/friends", response_model=Friend)
def add_friend(friend_create: FriendCreate):
    friend = Friend.from_orm(friend_create)
    with Session(engine) as session:
        session.add(friend)
        session.commit()
        session.refresh(friend)
    return friend

@app.get("/api/friends", response_model=list[Friend])
def get_friends():
    with Session(engine) as session:
        statement = select(Friend)
        results = session.exec(statement).all()
    return results

@app.post("/api/suggest-gift")
def suggest_gift(request: GiftRequest):
    name = request.name
    sentiment = request.sentiment

    # Suggest based on sentiment
    suggestions = {
        "close friend": [
            "Custom bracelet with initials",
            "Matching tote bag",
            "Spa night kit"
        ],
        "secret crush": [
            "Cute card with hint",
            "Floral-scented perfume",
            "Minimalist jewelry"
        ],
        "mentor": [
            "Thank-you candle",
            "Elegant pen",
            "Notebook with quote"
        ],
        "admired dancer": [
            "Fan art sketch",
            "Stage flowers",
            "Handwritten note + ribbon"
        ],
        # default fallback
        "default": [
            "Socks with their initials",
            "Dancewear store voucher"
        ]
    }

    options = suggestions.get(sentiment.lower(), suggestions["default"])
    suggestion = random.choice(options)

    return {
        "recipient": name,
        "sentiment": sentiment,
        "suggested_gift": suggestion
    }

