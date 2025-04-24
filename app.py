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
                "👋 Привет!\n\n"
                "Я — 🤖 *AI-ассистент по продажам* в компании AVALON — девелопере инвестиционной недвижимости на Бали.\n\n"
                "🏠 Расскажите, что вас интересует: проекты (OM, BUDDHA, TAO), доходность, документы, переезд.\n\n"
                "🧠 Я постараюсь помочь — а при необходимости вам напишет реальный менеджер.\n\n"
                "🌐 Можно писать на *любом языке* — я вас пойму."
            )
        elif language.startswith("uk"):
            welcome = (
                "👋 Привіт!\n\n"
                "Я — 🤖 *AI-асистент з продажу* компанії AVALON — девелопера інвестиційної нерухомості на Балі.\n\n"
                "🏠 Питайте про проєкти (OM, BUDDHA, TAO), прибутковість, документи або переїзд.\n\n"
                "🧠 Я допоможу вам — а за потреби з вами зв’яжеться справжній менеджер.\n\n"
                "🌐 Можна писати *будь-якою мовою* — я вас зрозумію."
            )
        else:
            welcome = (
                "👋 Hello and welcome!\n\n"
                "I'm the 🤖 *AI sales assistant* at AVALON — a real estate development company based in Bali.\n\n"
                "🏠 You can ask me anything about our investment projects (OM, BUDDHA, TAO), rental income, ROI, property management, or moving to Bali.\n\n"
                "🧠 I’ll do my best to help you — and if needed, one of our real sales managers will follow up personally.\n\n"
                "🌐 Feel free to write in *any language* — I’ll understand and reply accordingly."
            )
        send_telegram_message(chat_id, welcome)
        return "ok"

    if text.startswith("/addall "):
        if str(message.get("from", {}).get("id")) == "5275555034":
            new_prompt = text.replace("/addall ", "", 1).strip()
            with open("data/system_prompt.txt", "w", encoding="utf-8") as f:
                f.write(new_prompt)
            send_telegram_message(chat_id, "✅ System prompt fully replaced via /addall.")
        else:
            send_telegram_message(chat_id, "❌ You are not authorized to use this command.")
        return "ok"
    
    
    
    if text.strip() == "/prompt":
        if str(message.get("from", {}).get("id")) == "5275555034":
            try:
                with open("data/system_prompt.txt", "r", encoding="utf-8") as f:
                    prompt_text = f.read()
                send_telegram_message(chat_id, "📄 Current system prompt:

" + prompt_text)
            except Exception as e:
                send_telegram_message(chat_id, "❌ Failed to read system prompt.")
        else:
            send_telegram_message(chat_id, "❌ You are not authorized to use this command.")
        return "ok"
    
    
    


    if text.startswith("/add "):
        if str(message.get("from", {}).get("id")) == "5275555034":
            new_part = text.replace("/add ", "", 1).strip()
            with open("data/system_prompt.txt", "a", encoding="utf-8") as f:
                f.write("
" + new_part)
            send_telegram_message(chat_id, "✅ Text appended to system prompt via /add.")
        else:
            send_telegram_message(chat_id, "❌ You are not authorized to use this command.")
        return "ok"

    if text.startswith("/admin setprompt "):
        if str(message.get("from", {}).get("id")) == "5275555034":
            new_prompt = text.replace("/admin setprompt ", "", 1).strip()
            with open("data/system_prompt.txt", "w", encoding="utf-8") as f:
                f.write(new_prompt)
            send_telegram_message(chat_id, "✅ System prompt updated successfully.")
        else:
            send_telegram_message(chat_id, "❌ You are not authorized to use this command.")
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
