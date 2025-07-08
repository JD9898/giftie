from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from datetime import date

app = FastAPI()

class Friend(BaseModel):
    name: str
    birthday: date

# TEMPORARY in-memory store
db: List[Friend] = []

@app.post("/api/friends")
def add_friend(friend: Friend):
    db.append(friend)
    return {"message": "Friend added", "friend": friend}

@app.get("/api/friends")
def get_friends():
    return db
