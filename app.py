from flask import Flask, request
import openai
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")

def load_documents():
    folder = "data"
    context_parts = []
    for filename in os.listdir(folder):
        if filename.endswith(".txt"):
            with open(os.path.join(folder, filename), "r", encoding="utf-8") as f:
                context_parts.append(f.read())
    return "\n\n".join(context_parts)

documents_context = load_documents()

@app.route("/", methods=["GET"])
def home():
    return "Bot is running."

@app.route("/webhook", methods=["GET"])
def verify():
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if token == VERIFY_TOKEN:
        return challenge, 200
    return "Invalid verification token", 403

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    try:
        message = data["entry"][0]["changes"][0]["value"]["messages"][0]
        from_number = message["from"]
        user_text = message["text"]["body"]

        openai.api_key = OPENAI_API_KEY
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": f"Ты менеджер по продажам Avalon. Используй следующую информацию при ответах:\n\n{documents_context}"},
                {"role": "user", "content": user_text}
            ]
        )
        reply_text = response.choices[0].message.content

        url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"
        headers = {
            "Authorization": f"Bearer {WHATSAPP_TOKEN}",
            "Content-Type": "application/json"
        }
        payload = {
            "messaging_product": "whatsapp",
            "to": from_number,
            "type": "text",
            "text": {"body": reply_text}
        }

        requests.post(url, headers=headers, json=payload)

    except Exception as e:
        print("Error:", e)

    return "ok", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
