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

# Включаем логирование
logging.basicConfig(level=logging.INFO)

# Создаём бота и диспетчер
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Функция для запроса в OpenAI
async def ask_openai(prompt, use_gpt4=True):
    model = "gpt-4" if use_gpt4 else "gpt-3.5-turbo"
    
    try:
        response = await openai.ChatCompletion.acreate(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response["choices"][0]["message"]["content"]
    
    except openai.error.RateLimitError:
        if use_gpt4:  # Если GPT-4 дал лимит, пробуем GPT-3.5
            return await ask_openai(prompt, use_gpt4=False)
        return "❌ Лимит запросов исчерпан. Попробуйте позже или используйте GPT-3.5."

    except Exception as e:
        return f"❌ Ошибка: {e}"

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

    reply_text = await ask_openai(f"Проверь это домашнее задание и укажи ошибки: {text}")
    await message.answer(reply_text)

# Обычные вопросы (ChatGPT-режим)
@dp.message()
async def chat_with_gpt(message: Message):
    reply_text = await ask_openai(message.text)
    await message.answer(reply_text)

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
