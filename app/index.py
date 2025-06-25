from fastapi import FastAPI, Request, status
from contextlib import asynccontextmanager
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart

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

Добро пожаловать в мир изысканной красоты и непревзойденного стиля!

✨ Наша миссия:
Мы стремимся раскрыть вашу уникальную красоту, подчеркнуть индивидуальность и подарить уверенность в себе.

🎨 Наши услуги:
• Стрижки и укладки для любого типа волос
• Окрашивание и колорирование
• Уходовые процедуры для волос
• Макияж и визаж
• Маникюр и педикюр

👩‍🎨 Наши мастера:
Талантливая команда профессионалов с многолетним опытом и постоянным стремлением к совершенству. Мы следим за последними трендами и используем инновационные техники.

🌿 Наша атмосфера:
Погрузитесь в атмосферу уюта и релаксации. Каждый визит к нам - это не просто процедура, а настоящий ритуал красоты и заботы о себе.

💎 Почему выбирают нас:
• Индивидуальный подход к каждому клиенту
• Использование премиальной косметики
• Гарантия качества и результата
• Уютная и стильная обстановка
• Удобное расположение в центре города

Откройте для себя мир стиля вместе с "СТИЛЬ И ШАРМ"!
Запишитесь на консультацию прямо сейчас и сделайте первый шаг к вашему новому образу.

✨ Ваша красота - наше призвание! ✨
"""


async def greet_user(message: types.Message, is_new_user: bool = True) -> None:
    """
    Приветствует пользователя и отправляет соответствующее сообщение.
    """
    greeting = "Добро пожаловать" if is_new_user else "С возвращением"
    status = "Вы успешно зарегистрированы!" if is_new_user else "Рады видеть вас снова!"
    await message.answer(
        f"{greeting}, <b>{message.from_user.full_name}</b>! {status}\n"
        "Чем я могу помочь вам сегодня?",
        reply_markup=main_keyboard(user_id=message.from_user.id, first_name=message.from_user.first_name)
    )


# Обработчик команды /start
@dp.message(CommandStart())
async def command_start_handler(message: types.Message) -> None:
    await greet_user(message)


# Обработчик для кнопки "О нас"
@dp.message(lambda message: message.text == "О нас")
async def about_us_handler(message: types.Message) -> None:
    await message.answer(get_about_us_text())


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Код, выполняющийся при запуске приложения
    webhook_url = f"{WEBHOOK_URL}{WEBHOOK_PATH}"

    try:
        await bot.set_webhook(
            url=webhook_url,
            allowed_updates=dp.resolve_used_update_types(),
            drop_pending_updates=True
        )
        logger.info(f"Webhook успешно установлен: {webhook_url}")
    except Exception as e:
        logger.error(f"Ошибка при установке webhook: {e}")
        raise

    yield  # Приложение работает

    # Код, выполняющийся при завершении работы приложения
    try:
        await bot.delete_webhook()
        logger.info("Webhook успешно удален")
    except Exception as e:
        logger.error(f"Ошибка при удалении webhook: {e}")


# Инициализация FastAPI с методом жизненного цикла
app = FastAPI(lifespan=lifespan)


# Маршрут для проверки работоспособности
@app.get("/")
async def root():
    return {"status": "ok", "message": "Бот работает"}


# Маршрут для обработки вебхуков
# Webhook обработчик
@app.post("/webhook")
async def webhook(request: Request):
    try:
        json_data = await request.json()
        print("📡 Получен update:", json_data)
        update = Update.de_json(json_data, application.bot)
        await application.process_update(update)
        return {"status": "ok"}
    except Exception as e:
        print("❌ Ошибка при обработке webhook:", str(e))
        return {"status": "error", "message": str(e)}
