from flask import Flask, request
from openai import OpenAI
import os
import requests
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

TELEGRAM_TOKEN = "8116449369:AAEmgEZIcewrSDQ18-7CVbMntkZ4FMwey6k"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print("Send error:", e)

def load_prompt():
    try:
        with open("data/system_prompt.txt", "r", encoding="utf-8") as f:
            return f.read().strip()
    except:
        return ""

@app.route("/", methods=["POST"])
def telegram_webhook():
    data = request.get_json()
    print("📥 Update:", data)

    message = data.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    text = message.get("text", "")

    if not text:
        return "ok", 200

    if text.strip() == "/start":
        send_message(chat_id, "👋 Привет! Я AI-ассистент Avalon. Можете задать мне вопрос про проекты или инвестиции на Бали.")
        return "ok", 200

    try:
        system_prompt = load_prompt()
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ]
        )
        reply = response.choices[0].message.content
        send_message(chat_id, reply)
    except Exception as e:
        send_message(chat_id, f"⚠️ Ошибка: {e}")

    return "ok", 200

@app.route("/", methods=["GET"])
def home():
    return "Bot is running."

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
