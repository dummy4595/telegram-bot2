import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.filters import Command
from dotenv import load_dotenv
import os

# Загружаем токен из .env файла
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

# Включаем логирование
logging.basicConfig(level=logging.INFO)

# Создаем бота и диспетчер
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Команда /start
@dp.message(Command("start"))
async def start_handler(message: Message):
    await message.answer("Привет! Я ваш интеллектуальный Telegram-бот для школы 🎓")

# Обработчик сообщений
@dp.message()
async def echo_handler(message: Message):
    await message.answer(f"Вы сказали: {message.text}")

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
