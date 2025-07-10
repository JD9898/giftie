import random
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from datetime import date

app = FastAPI()

class Friend(BaseModel):
    name: str
    birthday: date

class GiftRequest(BaseModel):
    name: str
    birthday: date
    sentiment: str  # e.g., "secret crush", "mentor"
    

# TEMPORARY in-memory store
db: List[Friend] = []

@app.post("/api/friends")
def add_friend(friend: Friend):
    db.append(friend)
    return {"message": "Friend added", "friend": friend}

@app.get("/api/friends")
def get_friends():
    return db

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
    print("Options:", options)
    print("About to choose with random.choice")
    gifts = ["gift 1", "gift 2", "gift 3"]
    print(random.choice(gifts))

    suggestion = random.choice(options)

    return {
        "recipient": name,
        "sentiment": sentiment,
        "suggested_gift": suggestion
    }

