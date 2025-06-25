from fastapi import FastAPI, Request, status
from contextlib import asynccontextmanager
import logging
import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder

# Настройка логгирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Получение переменных окружения
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
WEBHOOK_PATH = "/webhook"



# Инициализация бота и диспетчера
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()


def get_about_us_text() -> str:
    return """
🌟 ЭЛЕГАНТНАЯ ПАРИКМАХЕРСКАЯ "СТИЛЬ И ШАРМ" 🌟
... [ваш текст] ...
"""


def main_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.button(text="О нас")
    builder.button(text="Услуги")
    builder.button(text="Контакты")
    builder.button(text="Записаться")
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)


async def safe_send_message(chat_id: int, text: str, **kwargs):
    """Безопасная отправка сообщения с обработкой ошибок"""
    try:
        await bot.send_message(chat_id=chat_id, text=text, **kwargs)
    except Exception as e:
        logger.error(f"Ошибка отправки сообщения: {e}")


@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await safe_send_message(
        message.chat.id,
        f"Привет, {message.from_user.full_name}! Чем могу помочь?",
        reply_markup=main_keyboard()
    )


@dp.message(lambda message: message.text == "О нас")
async def about_handler(message: types.Message):
    await safe_send_message(message.chat.id, get_about_us_text())


@dp.message()
async def other_messages(message: types.Message):
    await safe_send_message(
        message.chat.id,
        "Пожалуйста, используйте кнопки меню",
        reply_markup=main_keyboard()
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Установка вебхука при старте
    webhook_url = f"{WEBHOOK_URL}{WEBHOOK_PATH}"
    try:
        await bot.set_webhook(
            url=webhook_url,
            allowed_updates=dp.resolve_used_update_types(),
            drop_pending_updates=True
        )
        logger.info(f"Webhook установлен: {webhook_url}")
    except Exception as e:
        logger.error(f"Ошибка установки webhook: {e}")
        raise

    yield

    # Удаление вебхука при завершении
    try:
        await bot.delete_webhook()
        logger.info("Webhook удален")
    except Exception as e:
        logger.error(f"Ошибка удаления webhook: {e}")
    finally:
        # Явное закрытие сессии бота
        session = await bot.get_session()
        await session.close()


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def health_check():
    return {"status": "ok"}


@app.post(WEBHOOK_PATH)
async def webhook_handler(request: Request):
    try:
        
        # Создаем новую задачу для обработки обновления
        update_data = await request.json()
        asyncio.create_task(process_update(update_data))

        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Webhook error: {e}", exc_info=True)
        return {"status": "error"}, status.HTTP_500_INTERNAL_SERVER_ERROR


async def process_update(update_data: dict):
    """Отдельная асинхронная задача для обработки обновления"""
    try:
        update = types.Update.model_validate(update_data)
        await dp.feed_update(bot, update)
    except Exception as e:
        logger.error(f"Ошибка обработки обновления: {e}")
