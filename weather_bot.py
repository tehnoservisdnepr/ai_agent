import asyncio
import logging
import aiohttp
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message

# ИМПОРТ ИЗ ТВОЕГО ФАЙЛА
from analyze import get_weather_analysis

# --- НАСТРОЙКИ ---
TOKEN = "8744550835:AA..." # Твой токен
DOMOTICZ_URL = "http://100.96.33.208:8080/json.htm"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher()

async def get_domoticz_data():
    """Запрос данных с дачи"""
    params = {"type": "command", "param": "getdevices", "idx": "1"}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(DOMOTICZ_URL, params=params, timeout=5) as resp:
                if resp.status == 200:
                    return await resp.json()
    except:
        return None

@dp.message(Command("status"))
async def cmd_status(message: Message):
    # Вызываем обе функции
    data_domo = await get_domoticz_data()
    data_weather = await get_weather_analysis()
    
    res = ["📊 **Текущий статус:**\n"]
    
    if data_domo and "result" in data_domo:
        dev = data_domo["result"][0]
        res.append(f"🏠 **Дача:** `{dev.get('Temp')}°C` (вл. {dev.get('Humidity')}%)\n")
    
    if data_weather:
        res.append(f"🧲 **Магнитный индекс:** `{data_weather['kp']} Kp`")
        res.append(f"☀️ **УФ-излучение:** `{data_weather['uv']}`")
    
    await message.answer("\n".join(res), parse_mode="Markdown")

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())