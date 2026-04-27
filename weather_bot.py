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
        # Берем списки или текущие значения (защита от пустых данных)
        uv_list = res.get('uv_list', [])
        kp_list = res.get('kp_list', [])
        
        # Формируем стрелочки
        uv_trend = " ➔ ".join(map(str, uv_list)) if uv_list else str(res.get('uv_current', 'н/д'))
        kp_trend = " ➔ ".join(map(str, kp_list)) if kp_list else str(res.get('kp_current', 'н/д'))

        # 2. Формируем ПОЛНЫЙ контекст для ИИ (чтобы он видел цифры!)
        ai_context = (
            f"В Днепре сейчас {res['temp']}°C. "
            f"Прогноз Kp-индекса: {kp_trend}. "
            f"Прогноз УФ-индекса: {uv_trend}. "
            f"Максимальный УФ сегодня: {res.get('max_uv', 0)}. "
            f"Дай краткий совет по здоровью и электронике."
        )
        
        # Спрашиваем ИИ, передавая ему эти данные
        ai_opinion = await get_ai_verdict(ai_context)

        # 3. Собираем сообщение
        text = (
            f"📊 **ТЕКУЩИЙ СТАТУС:**\n\n"
            f"🌍 Днепр (Meteofor):\n"
            f"🌡 Температура: {res['temp']}°C\n"
            f"🧲 Kp-динамика: {kp_trend}\n"
            f"☀️ УФ-динамика: {uv_trend}\n\n"
            f"🤖 **АНАЛИЗ ИИ:**\n{ai_opinion}\n\n"
            f"🧐 _Помни: данные из аэропорта, верь своим чувствам!_"
        )
        
        await message.answer(text, parse_mode="Markdown")
    else:
        await message.answer("❌ Meteofor молчит...")
        
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

