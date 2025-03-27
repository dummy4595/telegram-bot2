import asyncio
import logging
import openai
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.filters import Command
from dotenv import load_dotenv
import aiohttp

# ✅ Загружаем переменные из .env
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# ✅ Проверяем, загружены ли ключи
if not BOT_TOKEN:
    raise ValueError("❌ Ошибка! Токен Telegram-бота не загружен. Проверь .env файл.")
if not OPENAI_API_KEY:
    raise ValueError("❌ Ошибка! API-ключ OpenAI не загружен. Проверь .env файл.")

# ✅ Настраиваем логирование
logging.basicConfig(level=logging.INFO)

# ✅ Настраиваем OpenAI API
openai.api_key = OPENAI_API_KEY

# ✅ Прокси (если нужно)
PROXY_LOGIN = os.getenv("PROXY_LOGIN")
PROXY_PASSWORD = os.getenv("PROXY_PASSWORD")
PROXY_IP = os.getenv("PROXY_IP")
PROXY_PORT = os.getenv("PROXY_PORT")

PROXY_URL = f"http://{PROXY_LOGIN}:{PROXY_PASSWORD}@{PROXY_IP}:{PROXY_PORT}" if PROXY_IP and PROXY_PORT and PROXY_LOGIN and PROXY_PASSWORD else None


# ✅ Функция создания бота и сессии
async def create_bot():
    connector = aiohttp.TCPConnector(ssl=False)  # Исправляем ошибку с loop
    session = aiohttp.ClientSession(connector=connector)

    bot = Bot(token=BOT_TOKEN, proxy=PROXY_URL) if PROXY_URL else Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    return bot, dp, session


# ✅ Проверяем загрузку ключей
print(f"BOT_TOKEN: {BOT_TOKEN[:5]}... (скрыт для безопасности)")
print(f"OPENAI_API_KEY: {OPENAI_API_KEY[:5]}... (скрыт для безопасности)")


# ✅ Обработчик команды /start
async def start_handler(message: Message):
    await message.answer("👋 Привет! Я ChatGPT-бот 🤖\nОтправь мне домашнее задание, и я помогу проверить его!")


# ✅ Обработчик команды /check (проверка ДЗ)
async def check_homework(message: Message):
    text = message.text.replace("/check", "").strip()

    if not text:
        await message.answer("⚠️ Пожалуйста, отправь текст домашнего задания после команды `/check`.")
        return

    try:
        response = await openai.ChatCompletion.acreate(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Ты — эксперт, который проверяет домашние задания."},
                {"role": "user", "content": f"Проверь это домашнее задание и укажи ошибки: {text}"}
            ]
        )
        reply_text = response["choices"][0]["message"]["content"]
    except openai.OpenAIError as e:
        reply_text = f"❌ Ошибка при проверке ДЗ: {str(e)}"
    except Exception as e:
        reply_text = f"❌ Общая ошибка: {str(e)}"

    await message.answer(reply_text)


# ✅ Обработчик сообщений через OpenAI
@dp.message()
async def chatgpt_handler(message: Message):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": message.text}],
            api_key=OPENAI_API_KEY
        )
        reply_text = response["choices"][0]["message"]["content"]
        await message.answer(reply_text)
    except Exception as e:
        await message.answer("❌ Ошибка при проверке ДЗ! Попробуй позже.")
        logging.error(f"Ошибка OpenAI: {e}")


# ✅ Запуск бота
async def main():
    bot, dp, session = await create_bot()

    # Регистрация обработчиков
    dp.message.register(start_handler, Command("start"))
    dp.message.register(check_homework, Command("check"))
    dp.message.register(chatgpt_handler)

    try:
        await dp.start_polling(bot)
    finally:
        await session.close()  # Корректное закрытие сессии


# ✅ Запуск
if __name__ == "__main__":
    import sys

    if sys.platform.startswith("win"):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    asyncio.run(main())
