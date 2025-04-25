from flask import Flask, request
import os

app = Flask(__name__)

@app.route("/", methods=["POST"])
def telegram_webhook():
    print("🟢 Webhook запущен и получил сообщение")
    data = request.get_json()
    print("📥 Update:", data)
    return "ok", 200

@app.route("/", methods=["GET"])
def home():
    return "Telegram bot is live!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
