from http.client import HTTPException
import random

from requests import session
from fastapi import FastAPI, Query, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
from datetime import date
from typing import Dict
from sqlmodel import Field, Session, SQLModel, create_engine, select
import stripe
from dotenv import load_dotenv
import os
from pydantic import BaseModel, EmailStr
import uuid
from playwright.sync_api import sync_playwright
import smtplib
from email.message import EmailMessage

load_dotenv()  # load from .env

app = FastAPI()
stripe.api_key = os.getenv("STRIPE_KEY")

class PostcardRequest(BaseModel):
    gift: str
    recipient: str


class FriendCreate(SQLModel):
    name: str
    birthday: date  # FastAPI will parse string → date here
    sentiment: str  # e.g., "close friend", "secret crush", "mentor", "admired dancer"
    email: EmailStr | None = None  # Optional email for sending postcard

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
        statement = select(GiftHistory).where(GiftHistory.recipient == recipient)
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
async def create_checkout_session(request: Request):
    body = await request.json()
    gift = body.get("gift")
    recipient = body.get("recipient")
    price = body.get("price")

    if not all([gift, recipient, price]):
        raise HTTPException(status_code=400, detail="Missing required fields")

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "gbp",
                        "product_data": {
                            "name": f"{gift} for {recipient}",
                        },
                        "unit_amount": int(float(price) * 100),  # e.g. £5.00 -> 500
                    },
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url="https://giftie.example.com/success",
            cancel_url="https://giftie.example.com/cancel",
        )
        return {"checkout_url": session.url}
    except Exception as e:
        print("Stripe error:", e)
        return JSONResponse(status_code=500, content={"error": str(e)})
    

@app.post("/api/generate-postcard")
def generate_postcard(data: PostcardRequest):
    output_dir = "postcards"
    os.makedirs(output_dir, exist_ok=True)

    html = f"""
    <html><body style="font-family:Arial;padding:40px;">
      <h2>Dear {data.recipient},</h2>
      <p>We thought you'd love this gift:</p>
      <h3>{data.gift}</h3>
      <p>From your Giftie app 🎁</p>
    </body></html>
    """

    filename = f"{uuid.uuid4().hex}.png"
    filepath = os.path.join(output_dir, filename)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.set_content(html)
        page.screenshot(path=filepath)
        browser.close()

    return { "image_url": f"/postcards/{filename}" }

class EmailPostcardRequest(BaseModel):
    recipient_email: EmailStr
    recipient_name: str
    image_url: str

@app.post("/api/email-postcard")
def email_postcard(data: EmailPostcardRequest):
    msg = EmailMessage()
    msg['Subject'] = f"A Giftie Postcard for {data.recipient_name}"
    msg['From'] = "youremail@example.com"
    msg['To'] = data.recipient_email

    msg.set_content(
        f"Hi {data.recipient_name},\n\nYou've received a postcard!\n\nView it here: {data.image_url}"
    )

    # Optional: embed image
    msg.add_alternative(f"""
    <html>
      <body>
        <p>Hi {data.recipient_name},</p>
        <p>You've received a postcard from Giftie:</p>
        <img src="{data.image_url}" style="max-width: 100%;" />
        <p>🎁</p>
      </body>
    </html>
    """, subtype='html')

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login("youremail@example.com", "your-app-password")
        smtp.send_message(msg)

    return {"message": "Postcard sent successfully!"}