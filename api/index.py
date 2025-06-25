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
TOKEN = "8037361730:AAGYYuoPNuewlq5ufMpaT0VBZFG5qDAgaAQ"
WEBHOOK_URL = "https://bot_aio.vercel.app"
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




# Инициализация FastAPI с методом жизненного цикла
app = FastAPI()


# Маршрут для проверки работоспособности
@app.get("/")
async def root():
    return {"status": "ok", "message": "Бот работает"}


# Маршрут для обработки вебхуков
# Webhook обработчик
@app.post("/webhook")
async def webhook(request: Request):
    try:
        update_json = await request.json()
        print("📡 Получен update:", update_json)
        update = types.Update.model_validate(update_json)

        # Передаем обновление в диспетчер
        await dp.feed_update(bot, update)
        return {"status": "ok"}
    except Exception as e:
        print("❌ Ошибка при обработке webhook:", str(e))
        return {"status": "error", "message": str(e)}
