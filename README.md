# 🎁 Giftie

Giftie is an agentic mobile app that intelligently suggests, tracks, and helps order personalized gifts for your friends — ballerinas or not! With minimal user input, it can manage gift ideas, birthdays, sentiments, and payments via Stripe or manual options like PayPal.

---

## 📱 Features

- Import and manage your friend list (with birthdays)
- Suggest gifts based on relationship sentiment
- Save gift suggestion history
- Initiate gift orders via Stripe (Apple/Google Pay supported)
- Manual payment links (PayPal.me / Revolut.me) also supported

---

## 🛠 Tech Stack

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

In the output, you'll find options to open the app in a

- [development build](https://docs.expo.dev/develop/development-builds/introduction/)
- [Android emulator](https://docs.expo.dev/workflow/android-studio-emulator/)
- [iOS simulator](https://docs.expo.dev/workflow/ios-simulator/)
- [Expo Go](https://expo.dev/go), a limited sandbox for trying out app development with Expo

You can start developing by editing the files inside the **app** directory. This project uses [file-based routing](https://docs.expo.dev/router/introduction).

## Get a fresh project

When you're ready, run:

```bash
npm run reset-project
```

This command will move the starter code to the **app-example** directory and create a blank **app** directory where you can start developing.

## Learn more

To learn more about developing your project with Expo, look at the following resources:

- [Expo documentation](https://docs.expo.dev/): Learn fundamentals, or go into advanced topics with our [guides](https://docs.expo.dev/guides).
- [Learn Expo tutorial](https://docs.expo.dev/tutorial/introduction/): Follow a step-by-step tutorial where you'll create a project that runs on Android, iOS, and the web.

## Join the community

Join our community of developers creating universal apps.

- [Expo on GitHub](https://github.com/expo/expo): View our open source platform and contribute.
- [Discord community](https://chat.expo.dev): Chat with Expo users and ask questions.
