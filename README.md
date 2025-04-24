# WhatsApp + OpenAI GPT Sales Bot (Avalon)

Backend-сервер для WhatsApp-бота, отвечающего через GPT-4o (OpenAI).

## Установка

1. Установите зависимости:
```
pip install -r requirements.txt
```

2. Проверьте переменные в `.env` (уже добавлен OpenAI ключ)

3. Запустите сервер:
```
python app.py
```

4. Задеплойте на Render/Railway и настройте Webhook в Meta Developer Console

## Переменные окружения

- `VERIFY_TOKEN` — токен для подтверждения webhook
- `WHATSAPP_TOKEN` — токен WhatsApp Cloud API
- `OPENAI_API_KEY` — ключ OpenAI GPT-4o
- `PHONE_NUMBER_ID` — ID номера WhatsApp
