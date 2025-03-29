import logging
import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message
from dotenv import load_dotenv
import openai

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

# ✅ Создаем бота и диспетчер
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ✅ Проверяем загрузку ключей
print(f"BOT_TOKEN: {BOT_TOKEN[:5]}... (скрыт для безопасности)")
print(f"OPENAI_API_KEY: {OPENAI_API_KEY[:5]}... (скрыт для безопасности)")

# ✅ Обработчик команды /start
@dp.message(Command("start"))
async def start_handler(message: Message):
    await message.answer("👋 Привет! Я ChatGPT-бот 🤖\nОтправь мне домашнее задание, и я помогу проверить его!")

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
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())


