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

# Приветственное сообщение
async def start(update, context):
    language = update.effective_user.language_code or "en"
    if language.startswith("ru"):
        welcome = (
            "👋 Привет!\n\n"
            "Я — 🤖 *AI-ассистент по продажам* в компании AVALON — девелопере инвестиционной недвижимости на Бали.\n\n"
            "🏠 Расскажите, что вас интересует: проекты (OM, BUDDHA, TAO), доходность, документы, переезд.\n\n"
            "🧠 Я постараюсь помочь — а при необходимости вам напишет реальный менеджер.\n\n"
            "🌐 Можно писать на *любом языке* — я вас пойму."
        )
    elif language.startswith("uk"):
        welcome = (
            "👋 Привіт!\n\n"
            "Я — 🤖 *AI-асистент з продажу* компанії AVALON — девелопера інвестиційної нерухомості на Балі.\n\n"
            "🏠 Питайте про проєкти (OM, BUDDHA, TAO), прибутковість, документи або переїзд.\n\n"
            "🧠 Я допоможу вам — а за потреби з вами зв’яжеться справжній менеджер.\n\n"
            "🌐 Можна писати *будь-якою мовою* — я вас зрозумію."
        )
    else:
        welcome = (
            "👋 Hello and welcome!\n\n"
            "I'm the 🤖 *AI sales assistant* at AVALON — a real estate development company based in Bali.\n\n"
            "🏠 You can ask me anything about our investment projects (OM, BUDDHA, TAO), rental income, ROI, property management, or moving to Bali.\n\n"
            "🧠 I’ll do my best to help you — and if needed, one of our real sales managers will follow up personally.\n\n"
            "🌐 Feel free to write in *any language* — I’ll understand and reply accordingly."
        )
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text=welcome, 
        parse_mode="Markdown"
    )

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
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("admin", setprompt))
    application.add_handler(CommandHandler("add", add_prompt))
    application.add_handler(CommandHandler("addall", setprompt))
    application.add_handler(CommandHandler("prompt", prompt))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    application.run_polling()