
import os
import openai
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

openai.api_key = os.getenv('OPENAI_API_KEY')

memory = ConversationBufferMemory(memory_key="history", return_messages=True)
chain = ConversationChain(llm=openai.ChatCompletion, memory=memory)

# FSM состояния
states = {}

# Функция отправки сообщений
async def send_message(update, context, text):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)

async def handle_message(update, context):
    user_id = update.effective_user.id
    user_text = update.message.text.lower()

    if user_id not in states:
        states[user_id] = "initial"

    # FSM логика
    if states[user_id] == "initial":
        response = chain.run(user_text)
        await send_message(update, context, response)
        if "встреча" in user_text or "звонок" in user_text:
            states[user_id] = "waiting_confirmation"
    elif states[user_id] == "waiting_confirmation":
        if "да" in user_text or "подтверждаю" in user_text:
            await send_message(update, context, "Отлично! Вот ваша ссылка на встречу: https://zoom.us/example")
            states[user_id] = "completed"
        else:
            await send_message(update, context, "Пожалуйста, подтвердите удобное время.")
    elif states[user_id] == "completed":
        await send_message(update, context, "Жду встречи! Если нужен перенос времени, сообщите.")

# Основной метод запуска
if __name__ == '__main__':
    application = ApplicationBuilder().token(os.getenv('TELEGRAM_TOKEN')).build()
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    application.run_polling()
