import asyncio
import logging
import aiohttp
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from analyze import get_weather_analysis

TOKEN = "8744550835:AAHb1VYtuMDqpJp6oyF8DUq-3plTMR1AZlk" 
DOMOTICZ_URL = "http://100.96.33.208:8080/json.htm"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=TOKEN)
dp = Dispatcher()

async def get_domoticz_data():
    params = {"type": "command", "param": "getdevices", "idx": "1"}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(DOMOTICZ_URL, params=params, timeout=5) as resp:
                if resp.status == 200: return await resp.json()
    except: return None

@dp.message(Command("status"))
async def cmd_status(message: Message):
    domo_task = asyncio.create_task(get_domoticz_data())
    weather_task = asyncio.create_task(get_weather_analysis())
    
    domo_data = await domo_task
    weather = await weather_task
    
    response = ["📊 **ТЕКУЩИЙ СТАТУС:**\n"]
    
    # Дача
    if domo_data and "result" in domo_data:
        dev = domo_data["result"][0]
        response.append(f"🏠 **Дача:** 🌡 `{dev.get('Temp')}°C` | 💧 `{dev.get('Humidity')}%`")
    else:
        response.append("🏠 **Дача:** ⚠️ Оффлайн")

    response.append("\n" + "—" * 15 + "\n")

    # Внешние данные
    if weather:
        kp = weather.get('kp', 0)
        uv = weather.get('uv', 0)
        kp_warn = "🔴 БУРЯ!" if kp >= 5 else "🟢 Спокойно"
        uv_warn = "⚠️ Нужна защита" if uv >= 3 else "✅ Безопасно"
        
        response.append(f"🌍 **Внешние данные (Днепр):**")
        response.append(f"🌡 По городу: `{weather.get('temp')}°C`")
        response.append(f"🧲 Kp: `{kp}` ({kp_warn})")
        response.append(f"☀️ УФ: `{uv}` ({uv_warn})")
        response.append(f"📊 Прогноз Kp: `{weather.get('kp_graph')}`")
    else:
        response.append("🌍 **Внешние данные:** ⚠️ Ошибка парсинга")

    await message.answer("\n".join(response), parse_mode="Markdown")

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())