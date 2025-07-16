from fastapi import FastAPI, Request
from pydantic import BaseModel
from datetime import timezone
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes, ConversationHandler,
)
import os
import uvicorn  
import httpx
from dotenv import load_dotenv
from perfect_gpt_client import *
from conversation_manager import ConversationManager

load_dotenv()

model = PerfectGPTClient()
MONGO_KEY = os.getenv("MONGO_KEY", "mongodb+srv://desgun4ik:bgB1t8KbEwToWc9d@cluster0.veevvji.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
conversation_manager = ConversationManager(MONGO_KEY)

# Проверка переменных окружения
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # Пример: https://your-project.up.railway.app

print(f"🔗 MongoDB: Подключение настроено")
print(f"🔑 Telegram Bot: {'✅ Готов' if TOKEN else '❌ Требуется TELEGRAM_BOT_TOKEN'}")

if not TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN не установлен")

app = FastAPI()

# Инициализация бота
application = Application.builder().token(TOKEN).build()

# Клавиатура для главного меню
main_keyboard = ReplyKeyboardMarkup(
    [["/ask", "/help"]],
    resize_keyboard=True,
    one_time_keyboard=False,
)

# ===== Обработчики команд =====
START, GET_NAME1 = range(2)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Привет! Я бот для рекомендательных систем.",
        reply_markup=main_keyboard,
    )
    api_check_user = f"https://swpdb-production.up.railway.app/users/{update.effective_user.id}"
    # if  requests.get(api_check_user).status_code == 200:
    #     await update.message.reply_text(
    #         "Вы уже зарегистрированы!",
    #         reply_markup=main_keyboard,
    #     )
    #     return ConversationHandler.END
    async with httpx.AsyncClient() as client:
        try:
            response_get_user = await client.get(api_check_user)
            print("вот твой код на повторный запрос", response_get_user.status_code)
            if response_get_user.status_code == 200:
                await update.message.reply_text(
                    "Вы уже зарегистрированы!",
                    reply_markup=main_keyboard,
                )
                return ConversationHandler.END
        except httpx.RequestError as e:
            await update.message.reply_text(
                "Ошибка при запросе на сервере. Обратитесь к администратору",
                reply_markup=main_keyboard,
            )
            return ConversationHandler.END
    await update.message.reply_text(
        "Пожалуйста, введите ваше имя: ",
        reply_markup=main_keyboard,
    )
    return GET_NAME1
async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Получение и сохранение имени пользователя"""
    user_name = update.message.text
    context.user_data['name'] = user_name  # Сохраняем имя


    payload_name_json = {
        "_id" : update.effective_user.id,
        "name" : user_name,
    }
    api_create_user = "https://swpdb-production.up.railway.app/users/"
    async with httpx.AsyncClient() as client:
        try:
            await client.post(api_create_user, json=payload_name_json)
            await update.message.reply_text(
                f"Отлично, {user_name}! Теперь вы можете пользоваться ботом.",
                reply_markup=main_keyboard,
            )
        except httpx.RequestError as e:
            await update.message.reply_text(
                "Ошибка при запросе на сервере. Обратитесь к администратору",
                reply_markup=main_keyboard,

            )

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Отмена ввода имени"""
    await update.message.reply_text(
        "Отмена",
        reply_markup=main_keyboard,
    )
    if 'conv_id' in context.user_data:
        del context.user_data['conv_id']

    return ConversationHandler.END
async def cancel_for_asking(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    command = update.message.text.split()[0]  # Получаем команду (/help, /start и т. д.)

    if command == "/help":
        
        await help_command(update, context)  # Предположим, что у вас есть функция help_command
    elif command == "/start":
        await start(update, context)
    elif command == "/ask":
        if 'conv_id' in context.user_data:
            del context.user_data['conv_id']
        return await ask(update, context)
    return ConversationHandler.END


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Доступные команды:\n"
        "/ask - задать вопрос\n"
        "/help - помощь\n"
        "/history - показать историю диалогов\n"
        "/clear - очистить историю диалогов\n"
        "/stats - показать статистику использования",
        reply_markup=main_keyboard,
    )

# async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     await update.message.reply_text(update.message.text, reply_markup=main_keyboard)



WAITING_FOR_MESSAGE = 1
async def ask(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    ask_keyboard = ReplyKeyboardMarkup([["Отмена"]], resize_keyboard=True, one_time_keyboard=True)
    context.user_data['last_message'] = None
    await update.message.reply_text("Напишите запрос! Чтобы завершить диалог, выберите другую команду или нажните /cancel", reply_markup=main_keyboard)
    async with httpx.AsyncClient() as client:
        api_create_conv = "https://swpdb-production.up.railway.app/conversations/"
        payload_conv_json = {
            "user_id": update.effective_user.id,
            "messages": []
        }
        try:
            response_create_conv = await client.post(api_create_conv, json=payload_conv_json)
            context.user_data['conv_id'] = response_create_conv.json().get("_id")
        except httpx.RequestError as e:
            await update.message.reply_text(
                "Ошибка на сервере -> обратитесь к админинстратору",
                reply_markup=main_keyboard,
            )
        return WAITING_FOR_MESSAGE
async def ask_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_text = update.message.text
    user_id = update.effective_user.id
    context.user_data['last_message'] = user_text
    global last_bot_response
    # Генерируем контекстный ответ с помощью ConversationManager
    response_to_bot = await conversation_manager.generate_contextual_response(user_id, user_text)
    print(response_to_bot)
    last_bot_response = response_to_bot  # Сохраняем ответ для возврата через /webhook
    await update.message.reply_text(
        response_to_bot,
        reply_markup=main_keyboard,
        parse_mode='Markdown',
    )
    
    # Сохраняем сообщения в API (для совместимости с существующей системой)
    api_add_message = f"https://swpdb-production.up.railway.app/conversations/{context.user_data['conv_id']}/messages"
    payload_add_message = {
        "sender" : "user",
        "text" : user_text,
        "time" : update.message.date.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
    }
    payload_add_message_bot = {
        "sender" : "bot",
        "text": response_to_bot,
        "time": update.message.date.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response_add_message_bot = await client.post(api_add_message, json=payload_add_message_bot)
        except httpx.RequestError as e:
            await update.message.reply_text(
                "Обратитесь к администратору(", 
                reply_markup=main_keyboard,
            )
    async with httpx.AsyncClient() as client:
        try:
            response_add_message = await client.post(api_add_message, json=payload_add_message)
        except httpx.RequestError as e:
            await update.message.reply_text(
                "Обратитесь к администратору(((", 
                reply_markup=main_keyboard,
            )
    return WAITING_FOR_MESSAGE

# ===== Новые команды для управления историей =====
async def history_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /history - показать историю диалогов"""
    user_id = update.effective_user.id
    
    try:
        # Получаем историю диалогов
        history = await conversation_manager.get_user_conversation_history(user_id, limit=10)
        
        if not history:
            await update.message.reply_text(
                "📝 История диалогов пуста\n\n"
                "У вас пока нет сохраненных диалогов. "
                "Начните задавать вопросы, и я буду запоминать нашу беседу!",
                reply_markup=main_keyboard,
            )
            return
        
        # Формируем сообщение с историей
        history_text = "📝 Ваша история диалогов:\n\n"
        
        for i, message in enumerate(history[-5:], 1):  # Показываем последние 5 сообщений
            sender = "👤 Вы" if message.get('sender') == 'user' else "🤖 Бот"
            text = message.get('text', '')[:100] + "..." if len(message.get('text', '')) > 100 else message.get('text', '')
            time = message.get('time', '')
            
            history_text += f"{i}. {sender}\n"
            history_text += f"💬 {text}\n"
            if time:
                history_text += f"🕐 {time}\n"
            history_text += "\n"
        
        history_text += f"📊 Всего сообщений: {len(history)}"
        
        await update.message.reply_text(history_text, reply_markup=main_keyboard)
        
    except Exception as e:
        await update.message.reply_text(
            "❌ Извините, произошла ошибка при получении истории диалогов.",
            reply_markup=main_keyboard,
        )

async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /clear - очистить историю диалогов"""
    user_id = update.effective_user.id
    
    try:
        # Очищаем историю
        success = await conversation_manager.clear_user_history(user_id)
        
        if success:
            await update.message.reply_text(
                "🗑️ История диалогов очищена\n\n"
                "Все ваши предыдущие диалоги удалены. "
                "Теперь я буду отвечать без учета предыдущего контекста.",
                reply_markup=main_keyboard,
            )
        else:
            await update.message.reply_text(
                "ℹ️ История уже пуста\n\n"
                "У вас нет сохраненных диалогов для очистки.",
                reply_markup=main_keyboard,
            )
        
    except Exception as e:
        await update.message.reply_text(
            "❌ Извините, произошла ошибка при очистке истории диалогов.",
            reply_markup=main_keyboard,
        )

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /stats - показать статистику использования"""
    user_id = update.effective_user.id
    
    try:
        # Получаем статистику
        stats = await conversation_manager.get_user_stats(user_id)
        
        if not stats or stats.get('total_messages', 0) == 0:
            await update.message.reply_text(
                "📊 Статистика использования\n\n"
                "У вас пока нет статистики. "
                "Начните задавать вопросы, и я буду отслеживать вашу активность!",
                reply_markup=main_keyboard,
            )
            return
        
        stats_text = "📊 Ваша статистика использования:\n\n"
        stats_text += f"💬 Всего сообщений: {stats.get('total_messages', 0)}\n"
        stats_text += f"👤 Ваших вопросов: {stats.get('user_messages', 0)}\n"
        stats_text += f"🤖 Ответов бота: {stats.get('bot_messages', 0)}\n"
        stats_text += f"📝 Диалогов: {stats.get('total_conversations', 0)}\n\n"
        
        # Добавляем рекомендации
        if stats.get('user_messages', 0) > 10:
            stats_text += "🎯 Вы активный пользователь! Продолжайте задавать вопросы."
        elif stats.get('user_messages', 0) > 5:
            stats_text += "👍 Хорошее начало! Попробуйте задать больше вопросов."
        else:
            stats_text += "🚀 Начните задавать вопросы, чтобы получить персонализированные ответы!"
        
        await update.message.reply_text(stats_text, reply_markup=main_keyboard)
        
    except Exception as e:
        await update.message.reply_text(
            "❌ Извините, произошла ошибка при получении статистики.",
            reply_markup=main_keyboard,
        )

# ===== Регистрация обработчиков =====
def register_handlers():
    conv_handler_start = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            GET_NAME1:[
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    get_name,
                )
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    application.add_handler(conv_handler_start)
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("history", history_command))
    application.add_handler(CommandHandler("clear", clear_command))
    application.add_handler(CommandHandler("stats", stats_command))

    ask_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("ask", ask)],
        states={
            WAITING_FOR_MESSAGE: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    ask_handler
                )
            ],
        },
        fallbacks=[
            CommandHandler("cancel", cancel),
            MessageHandler(filters.COMMAND, cancel_for_asking),
        ],
    )
    application.add_handler(ask_conv_handler)


register_handlers()
class SmartQuestionRequest(BaseModel):
    question: str
    user_id: int
class QuestionRequest(BaseModel):
    question: str
@app.post("/send_response")
async def send_response(request: QuestionRequest)-> str:
    """This endpoint send the question from the user to the LLM model"""
    answer = await model.generate_perfect_response(request.question)
    return answer
@app.post("/send_response_with_history")
async def send_response_with_history(request: SmartQuestionRequest)-> str:
    """This endpoint send the question from the user to the LLM model with history"""
    answer = await conversation_manager.generate_contextual_response(request.user_id, request.question)
    return answer
# ===== Вебхук и запуск =====
last_bot_response = None  # Глобальная переменная для хранения последнего ответа

@app.post("/webhook")
async def telegram_webhook(request: Request):
    try:
        data = await request.json()
        update = Update.de_json(data, application.bot)
        await application.process_update(update)
        return {"status": "ok"}
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return {"status": "error", "message": str(e)}

@app.get("/")
async def health_check():
    return {"status": "Bot is running"}

@app.on_event("startup")
async def startup():
    await application.initialize()
    await application.bot.set_webhook(f"{WEBHOOK_URL}/webhook")

@app.on_event("shutdown")
async def shutdown():
    await application.bot.delete_webhook()
    await application.shutdown()

# Запуск сервера (важно для Railway)
if __name__ == "__main__":
    import multiprocessing
    multiprocessing.freeze_support()
    
    port = int(os.getenv("PORT", 8000))  # Railway использует $PORT
    uvicorn.run(app, host="0.0.0.0", port=port, reload=False)
