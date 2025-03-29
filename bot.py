import asyncio
import logging
import openai
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.filters import Command
from dotenv import load_dotenv
import aiohttp

# Загружаем переменные окружения
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Прокси данные (если нужны)
PROXY_LOGIN = os.getenv("PROXY_LOGIN")
PROXY_PASSWORD = os.getenv("PROXY_PASSWORD")
PROXY_IP = os.getenv("PROXY_IP")
PROXY_PORT = os.getenv("PROXY_PORT")

# Формируем строку прокси (если данные есть)
if PROXY_IP and PROXY_PORT:
    PROXY_URL = f"http://{PROXY_IP}:{PROXY_PORT}"
else:
    PROXY_URL = None

# Настроим OpenAI API
openai.api_key = OPENAI_API_KEY

# Включаем логирование
logging.basicConfig(level=logging.INFO)

# Создаём бота и диспетчер
async def create_bot():
    # Настройка aiohttp Connector без прокси
    connector = aiohttp.TCPConnector(ssl=False)
    
    # Если прокси нужно с аутентификацией, создаем BasicAuth
    if PROXY_URL and PROXY_LOGIN and PROXY_PASSWORD:
        auth = aiohttp.BasicAuth(PROXY_LOGIN, PROXY_PASSWORD)
        session = aiohttp.ClientSession(connector=connector, proxy=PROXY_URL, proxy_auth=auth)
    else:
        session = aiohttp.ClientSession(connector=connector, proxy=PROXY_URL)
    
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    
    return bot, dp, session

# Обработчик команды /start
async def start_handler(message: Message):
    await message.answer("👋 Привет! Я бот ChatGPT в Telegram. Напиши мне что-нибудь, и я отвечу!\n\n"
                         "📌 Для проверки домашнего задания используй команду:\n"
                         "`/check [твой текст]`")

# Обработчик команды /check (проверка ДЗ)
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

# Обычные вопросы (ChatGPT-режим)
async def chat_with_gpt(message: Message):
    try:
        response = await openai.ChatCompletion.acreate(
            model="gpt-4",
            messages=[{"role": "user", "content": message.text}]
        )
        reply_text = response["choices"][0]["message"]["content"]
    except openai.OpenAIError as e:
        reply_text = f"❌ Ошибка: {str(e)}"
    except Exception as e:
        reply_text = f"❌ Общая ошибка: {str(e)}"

    await message.answer(reply_text)

# Запуск бота
async def main():
    bot, dp, session = await create_bot()

    # Регистрация обработчиков
    dp.message.register(start_handler, Command("start"))
    dp.message.register(check_homework, Command("check"))
    dp.message.register(chat_with_gpt)

    try:
        await dp.start_polling(bot)
    finally:
        await bot.close()  # Закрытие сессии бота
        await session.close()  # Закрытие сессии aiohttp

# Запуск
if __name__ == "__main__":
    import sys

    if sys.platform.startswith("win"):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    asyncio.run(main())
