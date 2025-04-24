# -*- coding: utf-8 -*-
import os
import threading
import requests
from flask import Flask, request

# Initialize Flask app
app = Flask(__name__)

# Read configuration from environment
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# Telegram API base URL for this bot
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/"

# Path to system prompt file in data directory
SYSTEM_PROMPT_PATH = "data/system_prompt.txt"

# Ensure data directory exists
os.makedirs(os.path.dirname(SYSTEM_PROMPT_PATH), exist_ok=True)

# In-memory chat history storage: {chat_id: [ {role: "...", content: "..."} ]}
histories = {}

# Function to send a message via Telegram API
def send_message(chat_id: int, text: str):
    url = TELEGRAM_API_URL + "sendMessage"
    # We send chat_id and text as JSON payload (Telegram will interpret it as a text message)
    payload = {"chat_id": chat_id, "text": text}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Failed to send message to chat {chat_id}: {e}")

# Function to call OpenAI Chat API (GPT-4 model) and get a response
def call_openai_api(messages: list) -> str:
    import openai  # import inside function to ensure the library is available
    openai.api_key = OPENAI_API_KEY
    try:
        response = openai.ChatCompletion.create(model="gpt-4", messages=messages)
        # Extract the assistant's reply text&#8203;:contentReference[oaicite:6]{index=6}
        return response.choices[0].message.content
    except Exception as e:
        # Log the error for debugging and return None
        print(f"OpenAI API call failed: {e}")
        return None

# Flask route for Telegram webhook
@app.route('/', methods=['POST'])
def telegram_webhook():
    update = request.get_json(force=True, silent=True)
    if not update:
        return "ok", 200  # Return 200 OK for non-JSON or empty payloads
    
    # We only handle incoming messages (ignore other update types like edited_message, callback_query, etc.)
    if "message" in update:
        msg = update["message"]
        chat_id = msg["chat"]["id"]
        user_id = msg["from"]["id"]
        text = msg.get("text", "")
        if not text:
            # Ignore non-text messages (stickers, photos, etc.)
            return "ok", 200

        # Handle commands (those starting with '/')
        if text.startswith("/"):
            # /start command: send greeting based on user language
            if text.strip().lower().startswith("/start"):
                # Determine user’s language (default to English if not provided)
                lang_code = str(msg["from"].get("language_code", "")).lower()
                if lang_code.startswith("ru"):
                    greeting = "Привет! Я чат-бот с искусственным интеллектом. Чем я могу помочь?"
                elif lang_code.startswith("uk"):
                    greeting = "Привіт! Я чат-бот зі штучним інтелектом. Чим я можу допомогти?"
                else:
                    greeting = "Hello! I'm an AI chatbot. How can I assist you today?"
                send_message(chat_id, greeting)

            # /addall command: replace system prompt (admin only)
            elif text.strip().lower().startswith("/addall"):
                if user_id != 5275555034:
                    send_message(chat_id, "Unauthorized command.")
                else:
                    # Get content after the command
                    new_content = text[len("/addall"):].lstrip()  # remove the command itself and any leading space
                    try:
                        with open(SYSTEM_PROMPT_PATH, "w", encoding="utf-8") as f:
                            f.write(new_content)
                        send_message(chat_id, "System prompt overwritten.")
                    except Exception as e:
                        send_message(chat_id, f"Error writing system prompt: {e}")

            # /add command: append to system prompt (admin only)
            elif text.strip().lower().startswith("/add"):
                if user_id != 5275555034:
                    send_message(chat_id, "Unauthorized command.")
                else:
                    # Extract content to append (if any)
                    append_text = text[len("/add"):].lstrip()
                    if append_text == "":
                        send_message(chat_id, "No text provided to add.")
                    else:
                        try:
                            # Determine if we need a newline before appending
                            need_newline = False
                            if os.path.isfile(SYSTEM_PROMPT_PATH):
                                # If file exists and is not empty and doesn't end with newline, we will add one
                                if os.path.getsize(SYSTEM_PROMPT_PATH) > 0:
                                    with open(SYSTEM_PROMPT_PATH, "rb") as f:  # open in binary to check last byte
                                        f.seek(-1, os.SEEK_END)
                                        last_char = f.read(1)
                                        if last_char not in [b"\n", b"\r"]:
                                            need_newline = True
                            # Append the text
                            with open(SYSTEM_PROMPT_PATH, "a", encoding="utf-8") as f:
                                if need_newline:
                                    f.write("\n")
                                f.write(append_text)
                            send_message(chat_id, "Text added to system prompt.")
                        except Exception as e:
                            send_message(chat_id, f"Error writing system prompt: {e}")

            # /prompt command: show current system prompt (admin only)
            elif text.strip().lower() == "/prompt":
                if user_id != 5275555034:
                    send_message(chat_id, "Unauthorized command.")
                else:
                    try:
                        with open(SYSTEM_PROMPT_PATH, "r", encoding="utf-8") as f:
                            prompt_content = f.read()
                        # If the prompt file is empty or only whitespace, inform that it's empty
                        if prompt_content.strip() == "":
                            send_message(chat_id, "(System prompt is empty)")
                        else:
                            send_message(chat_id, prompt_content)
                    except FileNotFoundError:
                        send_message(chat_id, "(System prompt is empty)")
                    except Exception as e:
                        send_message(chat_id, f"Error reading system prompt: {e}")

            else:
                # Unknown command or not handled explicitly
                send_message(chat_id, "Unknown command.")

        # Handle non-command messages (forward to OpenAI)
        else:
            # Load the current system prompt (if any)
            try:
                with open(SYSTEM_PROMPT_PATH, "r", encoding="utf-8") as f:
                    system_prompt = f.read().strip()
            except FileNotFoundError:
                system_prompt = ""
            except Exception as e:
                system_prompt = ""

            # Initialize history for this chat if not already
            if chat_id not in histories:
                histories[chat_id] = []
            # Append the new user message to history
            histories[chat_id].append({"role": "user", "content": text})

            # Build the messages payload for OpenAI API
            messages_payload = []
            if system_prompt:
                messages_payload.append({"role": "system", "content": system_prompt})
            # Include full conversation history for context
            messages_payload.extend(histories[chat_id])

            # Define a function to handle the OpenAI API call in a separate thread
            def process_openai_and_respond(chat_id, messages):
                # Call the OpenAI ChatCompletion API
                reply = call_openai_api(messages)
                if reply:
                    # Send the assistant's reply back to the user
                    send_message(chat_id, reply)
                    # Save the assistant reply in history for context
                    histories[chat_id].append({"role": "assistant", "content": reply})
                else:
                    # If API failed, notify the user
                    send_message(chat_id, "Sorry, I couldn't get a response.")

            # Start a new thread for the OpenAI call to avoid blocking the webhook response
            threading.Thread(target=process_openai_and_respond, args=(chat_id, messages_payload)).start()

    # Respond immediately to Telegram to confirm receipt of the update&#8203;:contentReference[oaicite:7]{index=7}
    return "ok", 200

# Run the Flask app (for local testing or when deployed without a separate WSGI server)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
