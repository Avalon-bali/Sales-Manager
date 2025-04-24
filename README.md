# WhatsApp GPT-4o Bot (Final)

Поддержка webhook, чтение файлов из папки data/, вывод контекста в GPT-4o.

## Как запустить на Render:

1. Залей репозиторий на GitHub
2. Создай Web Service на render.com
3. Укажи:
   - Build Command: pip install -r requirements.txt
   - Start Command: python app.py
4. Добавь переменные окружения:
   - VERIFY_TOKEN=avalon-secret
   - WHATSAPP_TOKEN=...
   - OPENAI_API_KEY=...
   - PHONE_NUMBER_ID=...

5. Проверь webhook:
https://your-domain/webhook?hub.verify_token=avalon-secret&hub.challenge=1234
