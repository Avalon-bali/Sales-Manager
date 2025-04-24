import os
from telegram.ext import ApplicationBuilder, MessageHandler, filters
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.schema import SystemMessage, HumanMessage

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

llm = ChatOpenAI(api_key=OPENAI_API_KEY, model="gpt-4o")

memory = ConversationBufferMemory(return_messages=True)

PROMPT = """
Ты — AI консультант отдела продаж AVALON.
- Всегда представляйся именно так.
- Общайся только на темы: Avalon, инвестиционная недвижимость на Бали (проекты OM / BUDDHA / TAO), жизнь на Бали, релокация, инвестиции.
- Если пользователь задаёт вопросы на другие темы (например, Испания), вежливо возвращай разговор к указанным темам.
- Никогда не упоминай, что ты бот или ИИ.
- Общайся максимально естественно, как профессиональный консультант по продажам.
- Основная цель: назначение звонка в Zoom/Google Meet в течение 2-3 сообщений.
"""

async def send_message(update, context, text):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)

async def handle_message(update, context):
    user_text = update.message.text.strip()

    history = memory.load_memory_variables({})["history"]
    
    messages = [SystemMessage(content=PROMPT)] + history + [HumanMessage(content=user_text)]

    response = llm.invoke(messages).content

    memory.save_context({"input": user_text}, {"output": response})

    await send_message(update, context, response)

if __name__ == '__main__':
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    application.run_polling()