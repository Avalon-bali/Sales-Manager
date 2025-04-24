# Telegram GPT-4o Bot — FINAL

Функциональность:
- Поддержка GPT-4o
- Обработка команды /start
- Чтение контекста из папки data/
- Логирование всех входящих сообщений
- Работает с OpenAI < 1.0.0

## Установка

1. Залей репозиторий на GitHub
2. Создай Web Service на Render
3. Укажи:
- Build command: pip install -r requirements.txt
- Start command: python app.py
4. Добавь переменные окружения:
- OPENAI_API_KEY=your-openai-key

## Установка Webhook
https://api.telegram.org/bot<ТВОЙ_ТОКЕН>/setWebhook?url=https://<ТВОЙ_ДОМЕН>/<ТВОЙ_ТОКЕН>
