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
    language = message.get("from", {}).get("language_code", "en")

    if not chat_id:
        return "no chat_id", 400

    if text.strip() == "/start":
        if language.startswith("ru"):
            welcome = (
                "👋 Привет!

"
                "Я — 🤖 *AI-ассистент по продажам* в компании AVALON — девелопере инвестиционной недвижимости на Бали.

"
                "🏠 Расскажите, что вас интересует: проекты (OM, BUDDHA, TAO), доходность, документы, переезд.

"
                "🧠 Я постараюсь помочь — а при необходимости вам напишет реальный менеджер.

"
                "🌐 Можно писать на *любом языке* — я вас пойму."
            )
        elif language.startswith("uk"):
            welcome = (
                "👋 Привіт!

"
                "Я — 🤖 *AI-асистент з продажу* компанії AVALON — девелопера інвестиційної нерухомості на Балі.

"
                "🏠 Питайте про проєкти (OM, BUDDHA, TAO), прибутковість, документи або переїзд.

"
                "🧠 Я допоможу вам — а за потреби з вами зв’яжеться справжній менеджер.

"
                "🌐 Можна писати *будь-якою мовою* — я вас зрозумію."
            )
        else:
            welcome = (
                "👋 Hello and welcome!

"
                "I'm the 🤖 *AI sales assistant* at AVALON — a real estate development company based in Bali.

"
                "🏠 You can ask me anything about our investment projects (OM, BUDDHA, TAO), rental income, ROI, property management, or moving to Bali.

"
                "🧠 I’ll do my best to help you — and if needed, one of our real sales managers will follow up personally.

"
                "🌐 Feel free to write in *any language* — I’ll understand and reply accordingly."
            )
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
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    r = requests.post(url, json=payload)
    print("📤 Ответ отправлен:", r.status_code, r.text)

@app.route("/", methods=["GET"])
def home():
    return "Telegram GPT bot is running."

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
