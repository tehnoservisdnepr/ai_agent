import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# Твои рабочие модули из списка ls -l
from analyze import get_weather_analysis
from ai_engine import get_ai_verdict
from api_token import TELEGRAM_TOKEN

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Привет! Гляжу в Meteofor, спрашиваю Llama 3. Жми /status")

@dp.message(Command("status"))
async def cmd_status(message: types.Message):
    # 1. Тянем погоду через analyze.py
    res = await get_weather_analysis()
    
    if res:
        # 2. Спрашиваем ИИ через ai_engine.py
        ai_opinion = await get_ai_verdict("OK")

        # 3. Собираем сообщение
        text = (
            f"📊 **ТЕКУЩИЙ СТАТУС:**\n\n"
            f"🌍 Днепр (Meteofor):\n"
            f"🌡 Температура: {res['temp']}°C\n"
            f"🧲 Kp-индекс: {res['kp']}\n"
            f"☀️ УФ-индекс: {res['uv']}\n\n"
            f"🤖 **АНАЛИЗ ИИ:**\n{ai_opinion}\n\n"
            f"🧐 _Помни: данные из аэропорта, верь своим чувствам!_"
        )
        
        await message.answer(text)
    else:
        await message.answer("❌ Meteofor молчит...")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

