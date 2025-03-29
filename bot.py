import asyncio
import logging
import openai
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.filters import Command
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Создаём OpenAI клиент
client = openai.OpenAI(api_key=OPENAI_API_KEY)

# Включаем логирование
logging.basicConfig(level=logging.INFO)

# Создаём бота и диспетчер
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Обработчик команды /start
@dp.message(Command("start"))
async def start(message: Message):
    await message.answer("👋 Привет! Я бот ChatGPT в Telegram.\n\n"
                         "📌 Для проверки домашнего задания используй команду:\n"
                         "`/check [твой текст]`")

# Обработчик команды /check (проверка ДЗ)
@dp.message(Command("check"))
async def check_homework(message: Message):
    text = message.text.replace("/check", "").strip()
    
    if not text:
        await message.answer("⚠️ Пожалуйста, отправь текст домашнего задания после команды `/check`.")
        return

    try:
        response = client.chat.completions.create(
            model="gpt-4",  # Используем GPT-4
            messages=[
                {"role": "system", "content": "Ты — эксперт, который проверяет домашние задания."},
                {"role": "user", "content": f"Проверь это домашнее задание и укажи ошибки: {text}"}
            ]
        )
        reply_text = response.choices[0].message.content
    except openai.OpenAIError as e:
        reply_text = f"❌ Ошибка при проверке ДЗ: {e}"
    except Exception as e:
        reply_text = f"❌ Неизвестная ошибка: {e}"

    await message.answer(reply_text)

# Обычные вопросы (ChatGPT-режим)
@dp.message()
async def chat_with_gpt(message: Message):
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": message.text}]
        )
        reply_text = response.choices[0].message.content
    except openai.OpenAIError as e:
        reply_text = f"❌ Ошибка: {e}"
    except Exception as e:
        reply_text = f"❌ Неизвестная ошибка: {e}"

    await message.answer(reply_text)

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
