from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
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
import openai
import base64

load_dotenv()  # load from .env

app = FastAPI()
stripe.api_key = os.getenv("STRIPE_KEY")

class PostcardRequest(BaseModel):
    gift: str
    recipient: str
    # recipient_email: EmailStr


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

class EmailPostcardRequest(BaseModel):
    recipient_email: EmailStr
    recipient_name: str
    image_url: str

class PostcardPrompt(BaseModel):
    recipient: str
    message: str
    theme: str = 'birthday'

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

    send_email_postcard()
    return { "image_url": f"/postcards/{filename}" }

def send_email_postcard():
    sender = os.getenv("SMTP_USER")
    recipient = sender  # Send to yourself for testing

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Test Email from Giftie"
    msg["From"] = sender
    msg["To"] = recipient

    text = "Hi,\nThis is a test email from Giftie."
    html = """
    <html>
    <body>
        <p>Hello,<br>
        This is a <b>test</b> email from <i>Giftie</i>.
        </p>
    </body>
    </html>
    """

    # Encode both parts in UTF-8
    part1 = MIMEText(text.encode('utf-8'), "plain", "utf-8")
    part2 = MIMEText(html.encode('utf-8'), "html", "utf-8")

    msg.attach(part1)
    msg.attach(part2)

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, os.getenv("SMTP_PASS"))
            server.sendmail(sender, recipient, msg.as_string())
        print("✅ Email sent successfully.")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_personal_message(prompt: str) -> str:
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are a friendly and creative postcard writer. Keep it short, warm, and heartfelt."
                },
                {
                    "role": "user",
                    "content": f"Write a short postcard message for: {prompt}"
                }
            ],
            max_tokens=100,
            temperature=0.8,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print("OpenAI error:", e)
        return "Hope this little surprise brightens your day! 🎁"

def get_styled_html(recipient: str, message: str, theme: str = "birthday") -> str:
    decorations = {
        "birthday": {
            "bg_color": "#FFF5E1",
            "emoji": "🎉🎂🎈",
            "image": "https://i.imgur.com/Fn1jftF.png",  # birthday balloons
        },
        "friendship": {
            "bg_color": "#E6F7FF",
            "emoji": "🤗💖✨",
            "image": "https://i.imgur.com/9xR5z7m.png",  # hearts
        },
        "love": {
            "bg_color": "#FFE6E6",
            "emoji": "💌❤️🌹",
            "image": "https://i.imgur.com/x1P5sB8.png",  # romantic
        }
    }

    style = decorations.get(theme, decorations["birthday"])

    return f"""
    <html>
    <head>
      <link href="https://fonts.googleapis.com/css2?family=Quicksand:wght@500&display=swap" rel="stylesheet">
      <style>
        body {{
          font-family: 'Quicksand', sans-serif;
          background: linear-gradient(to bottom right, #fceabb, #f8b500);
          width: 600px;
          height: 400px;
          position: relative;
          padding: 40px;
          box-sizing: border-box;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          text-align: center;
        }}
        .image-decor {{
          position: absolute;
          top: 0;
          left: 0;
          width: 600px;
          height: 400px;
          opacity: 0.2;
          z-index: 0;
        }}
        .content {{
          z-index: 1;
        }}
        h1 {{
          font-size: 28px;
          margin-bottom: 10px;
        }}
        p {{
          font-size: 18px;
          color: #333;
        }}
      </style>
    </head>
    <body>
      <div class="content">
        <h1>{style['emoji']} Dear {recipient},</h1>
        <p>{message}</p>
        <p style="margin-top: 20px;">From your Giftie app 🎁</p>
      </div>
    </body>
    </html>
    """

def get_unsplash_background(gift: str) -> str:
    keywords = {
        "birthday": "birthday",
        "chocolate": "dessert",
        "flowers": "flowers",
        "book": "reading",
        "coffee": "coffee",
        "love": "romantic",
        "jewellery": "luxury",
    }

    for keyword, theme in keywords.items():
        if keyword in gift.lower():
            return f"https://source.unsplash.com/1200x800/?{theme}"

    # default fallback
    return "https://source.unsplash.com/1200x800/?gift"

def get_base64_image(path: str) -> str:
    with open(path, "rb") as img_file:
        encoded = base64.b64encode(img_file.read()).decode("utf-8")
        return f"data:image/png;base64,{encoded}"

@app.post("/api/generate-custom-postcard")
def generate_custom_postcard(prompt: PostcardPrompt):
    output_dir = "postcards"
    os.makedirs(output_dir, exist_ok=True)

    html = get_styled_html(prompt.recipient, prompt.message, prompt.theme)

    filename = f"{uuid.uuid4().hex}.png"
    filepath = os.path.join(output_dir, filename)

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            context = browser.new_context(
                viewport={"width": 600, "height": 400},  
                device_scale_factor=2.0  
            )
            page = context.new_page()
            page.set_content(html)
            page.screenshot(path=filepath, full_page=True)
            browser.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to render postcard: {e}")

    return {"image_url": f"/postcards/{filename}"}
