from flask import Flask, request
from openai import OpenAI
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

TELEGRAM_TOKEN = "8116449369:AAGBPph9JSaUGVpS731xGsAXxthQYFrthpA"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

def load_documents():
    folder = "data"
    context_parts = []
    for filename in os.listdir(folder):
        if filename.endswith(".txt") and filename != "system_prompt.txt":
            with open(os.path.join(folder, filename), "r", encoding="utf-8") as f:
                context_parts.append(f.read())
    return "\n\n".join(context_parts)

def load_system_prompt():
    with open("data/system_prompt.txt", "r", encoding="utf-8") as f:
        return f.read()

documents_context = load_documents()
system_prompt = load_system_prompt()

@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def telegram_webhook():
    data = request.get_json()
    print("🔔 Входящее сообщение от Telegram:", data)

    message = data.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    text = message.get("text", "")

    if not chat_id:
        return "no chat_id", 400

    if text.strip() == "/start":
        welcome = "👋 Привет! Я — менеджер по продажам Avalon.\nМожете спросить про любой проект, договор или условия инвестиций."
        send_telegram_message(chat_id, welcome)
        return "ok"

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": f"{system_prompt}\n\n{documents_context}"},
                {"role": "user", "content": text}
            ]
        )
        reply = response.choices[0].message.content
    except Exception as e:
        reply = f"Произошла ошибка при обращении к OpenAI: {e}"
        print("❌ Ошибка GPT:", e)

    send_telegram_message(chat_id, reply)
    return "ok"

def send_telegram_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    r = requests.post(url, json=payload)
    print("📤 Ответ отправлен:", r.status_code, r.text)

@app.route("/", methods=["GET"])
def home():
    return "Telegram GPT bot is running."

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
