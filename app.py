import os
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.schema import SystemMessage, HumanMessage

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

llm = ChatOpenAI(api_key=OPENAI_API_KEY, model="gpt-4o")
memory = ConversationBufferMemory(return_messages=True)

PROMPT_PATH = "system_prompt.txt"

def load_prompt():
    if os.path.exists(PROMPT_PATH):
        with open(PROMPT_PATH, 'r', encoding='utf-8') as file:
            return file.read().strip()
    return ""

async def send_message(update, context, text):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)

async def handle_message(update, context):
    user_text = update.message.text.strip()
    history = memory.load_memory_variables({})["history"]
    prompt = load_prompt()
    messages = [SystemMessage(content=prompt)] + history + [HumanMessage(content=user_text)]
    response = llm.invoke(messages).content
    memory.save_context({"input": user_text}, {"output": response})
    await send_message(update, context, response)

# Команды
async def setprompt(update, context):
    new_prompt = " ".join(context.args)
    with open(PROMPT_PATH, 'w', encoding='utf-8') as file:
        file.write(new_prompt)
    await send_message(update, context, "System prompt успешно обновлён.")

async def add_prompt(update, context):
    addition = " ".join(context.args)
    with open(PROMPT_PATH, 'a', encoding='utf-8') as file:
        file.write("\n" + addition)
    await send_message(update, context, "Текст успешно добавлен к текущему промпту.")

async def prompt(update, context):
    current_prompt = load_prompt()
    await send_message(update, context, f"📄 Текущий промпт:\n{current_prompt}")

if __name__ == '__main__':
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("admin", setprompt))
    application.add_handler(CommandHandler("add", add_prompt))
    application.add_handler(CommandHandler("addall", setprompt))
    application.add_handler(CommandHandler("prompt", prompt))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    application.run_polling()