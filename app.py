import os
from telegram.ext import ApplicationBuilder, MessageHandler, filters
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage
from langchain.memory import ConversationBufferMemory

openai_api_key = os.getenv('OPENAI_API_KEY')

llm = ChatOpenAI(api_key=openai_api_key, model="gpt-4o")
memory = ConversationBufferMemory(return_messages=True)

states = {}

async def send_message(update, context, text):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)

async def handle_message(update, context):
    user_id = update.effective_user.id
    user_text = update.message.text.lower()

    if user_id not in states:
        states[user_id] = "initial"

    history = memory.load_memory_variables({})["history"]
    messages = history + [HumanMessage(content=user_text)]

    response = llm(messages).content
    memory.save_context({"input": user_text}, {"output": response})

    if states[user_id] == "initial":
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

if __name__ == '__main__':
    application = ApplicationBuilder().token(os.getenv('TELEGRAM_TOKEN')).build()
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    application.run_polling()