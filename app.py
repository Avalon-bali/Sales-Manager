from flask import Flask, request
from openai import OpenAI
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

TELEGRAM_TOKEN = "8116449369:AAEmgEZIcewrSDQ18-7CVbMntkZ4FMwey6k"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()
    print("🔔 Incoming data:", data)
    return "ok", 200

@app.route("/", methods=["GET"])
def index():
    return "Telegram bot is live!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
