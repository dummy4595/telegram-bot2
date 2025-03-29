import logging
import openai
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.utils import executor
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Настраиваем OpenAI API
openai.api_key = OPENAI_API_KEY

# Включаем логирование
logging.basicConfig(level=logging.INFO)

# Создаём бота
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# Обработчик команды /start
@dp.message_handler(commands=["start"])
async def start(message: Message):
    await message.reply("Привет! Я бот ChatGPT в Telegram. Напиши мне что-нибудь, и я отвечу!\n\n"
                        "Если хочешь, чтобы я проверил твоё ДЗ, отправь его с командой /check.")

# Обработчик проверки ДЗ
@dp.message_handler(commands=["check"])
async def check_homework(message: Message):
    text = message.text.replace("/check", "").strip()
    
    if not text:
        await message.reply("Пожалуйста, отправь текст домашнего задания после команды /check.")
        return

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",  # Можно заменить на gpt-3.5-turbo
            messages=[
                {"role": "system", "content": "Ты — эксперт, который проверяет домашние задания."},
                {"role": "user", "content": f"Проверь это домашнее задание и укажи ошибки: {text}"}
            ]
        )
        reply_text = response["choices"][0]["message"]["content"]
    except Exception as e:
        reply_text = f"Ошибка при проверке ДЗ: {e}"

    await message.reply(reply_text)

# Обычные вопросы (ChatGPT-режим)
@dp.message_handler()
async def chat_with_gpt(message: Message):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": message.text}]
        )
        reply_text = response["choices"][0]["message"]["content"]
    except Exception as e:
        reply_text = f"Ошибка: {e}"

    await message.reply(reply_text)

# Запуск бота
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
