import asyncio
import aiohttp
import math
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# Настройки
TOKEN = "8744550835:AAHb1VYtuMDqpJp6oyF8DUq-3plTMR1AZlk"
DOMOTICZ_URL = "http://100.96.33.208:8080/json.htm"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher()

async def get_data_from_domoticz():
    params = {"type": "devices", "rid": "1"}
    # Тайм-аут 5 секунд — если Domoticz молчит, не будем ждать вечно
    timeout = aiohttp.ClientTimeout(total=5)
    
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(DOMOTICZ_URL, params=params) as response:
            return await response.json()

@dp.message(Command("status"))
async def cmd_status(message: types.Message):
    try:
        data = await get_data_from_domoticz()
        if data.get("status") == "OK":
            dev = data["result"][0]
            t, h = float(dev["Temp"]), float(dev["Humidity"])
            sig = dev.get("SignalLevel", "N/A")
            
            # Расчет точки росы
            a, b = 17.27, 237.7
            alpha = ((a * t) / (b + t)) + math.log(h/100.0)
            dew = round((b * alpha) / (a - alpha), 2)

            await message.answer(f"🏠 **Данные с дачи:**\n🌡 {t}°C | 💧 {h}% | 🥤 {dew}°C\n📶 Сигнал: {sig}/12")
        else:
            await message.answer("⚠️ Ошибка данных от Domoticz.")
    except Exception as e:
        await message.answer(f"❌ Бот не достучался до сервера: {str(e)[:50]}")

async def main():
    print("🚀 Бот запущен (надежный режим)...")
    # Перезапуск при ошибках + игнорирование старых команд
    while True:
        try:
            await dp.start_polling(bot, skip_updates=True, polling_timeout=20)
        except Exception as e:
            logging.error(f"Ошибка в polling: {e}. Рестарт через 5 сек...")
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())