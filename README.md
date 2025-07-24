# Giftie 🎁

Giftie is an agentic mobile app that intelligently suggests, tracks, and helps order personalized gifts for your friends! With minimal user input, it can manage gift ideas, birthdays, sentiments, and payments via Stripe.

---

## Features 📱

- Import and manage your friend list with birthdays
- Suggest gifts based on relationship sentiment
- Save gift suggestion history
- Initiate gift orders via Stripe (Apple/Google Pay supported)

---

## Tech Stack 🛠

- **Frontend**: React Native (via [Expo](https://expo.dev/))
- **Backend**: FastAPI
- **Database**: SQLite (via SQLModel)
- **Payments**: Stripe Checkout (Apple Pay & Google Pay support)

---

## Run the backend

```bash
cd giftie-backend
python3 -m venv env # skip if you have aleady build the virtual environment
source env/bin/activate
pip install -r requirements.txt # skip if you have aleady build the virtual environment
```

## Run the fastAPI server

```bash
uvicorn main:app --reload
```


## Get started

1. Install dependencies

```bash
npm install
```

2. Start the app

```bash
npx expo start
```

3. Run the backend

```bash
uvicorn main:app --reload
```

4. Run ngrok

```bash
ngrok http 8000
```

Then change the BACKEND_URL into the location where this is running. e.g. https://86ca108cc09b.ngrok-free.app