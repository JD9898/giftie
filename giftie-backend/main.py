from http.client import HTTPException
import random
from fastapi import FastAPI, Query, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List
from datetime import date
from typing import Dict
from sqlmodel import Field, Session, SQLModel, create_engine, select
import stripe
from dotenv import load_dotenv
import os

load_dotenv()  # load from .env

app = FastAPI()
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

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

@app.post("/api/create-checkout-session")
def create_checkout_session(recipient: str, gift: str, price: float):
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "gbp",
                        "product_data": {"name": f"Gift for {recipient}: {gift}"},
                        "unit_amount": int(price * 100),  # price in pence
                    },
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url="https://your-frontend.com/success",
            cancel_url="https://your-frontend.com/cancel",
        )
        return {"checkout_url": session.url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/create-checkout-session")
async def create_checkout_session(request: Request):
    data = await request.json()
    recipient = data.get("recipient")
    gift = data.get("gift")
    price = data.get("price", 5.00)  # £5 default

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "gbp",
                    "product_data": {
                        "name": f"Gift for {recipient}: {gift}",
                    },
                    "unit_amount": int(price * 100),  # £5 → 500 pence
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url="https://example.com/success",
            cancel_url="https://example.com/cancel",
        )
        return JSONResponse({"checkout_url": session.url})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
