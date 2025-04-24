import os
import openai
import requests
from flask import Flask, request
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

TELEGRAM_TOKEN = "7938243060:AAFIAUO5SjHRmDClpE_pHxCdEmFczKsQc4Q"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def load_documents():
    folder = "data"
    context_parts = []
    for filename in os.listdir(folder):
        if filename.endswith(".txt"):
            with open(os.path.join(folder, filename), "r", encoding="utf-8") as f:
                context_parts.append(f.read())
    return "\n\n".join(context_parts)

documents_context = load_documents()

@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json()
    message = data["message"]
    chat_id = message["chat"]["id"]
    text = message.get("text", "")

    openai.api_key = OPENAI_API_KEY
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": f"Ты менеджер по продажам Avalon. Используй следующую информацию при ответах:\n\n{documents_context}"},
            {"role": "user", "content": text}
        ]
    )
    reply = response.choices[0].message.content

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": reply}
    requests.post(url, json=payload)

    return "ok"

@app.route("/", methods=["GET"])
def home():
    return "Telegram bot running."

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
