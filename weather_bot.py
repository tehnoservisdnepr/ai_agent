import asyncio
import aiohttp
import math
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

TOKEN = "8744550835:AAHb1VYtuMDqpJp6oyF8DUq-3plTMR1AZlk"
DOMOTICZ_URL = "http://100.96.33.208:8080/json.htm"

bot = Bot(token=TOKEN)
dp = Dispatcher()

def calc_dew_point(temp, hum):
    a, b = 17.27, 237.7
    alpha = ((a * temp) / (b + temp)) + math.log(hum/100.0)
    return round((b * alpha) / (a - alpha), 2)

@dp.message(Command("status"))
async def cmd_status(message: types.Message):
    # Запрос данных по конкретному ID датчика (rid=1)
    params = {"type": "devices", "rid": "1"}
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(DOMOTICZ_URL, params=params) as response:
                data = await response.json()
                
                if data.get("status") == "OK" and "result" in data:
                    dev = data["result"][0]
                    t = float(dev.get("Temp", 0))
                    h = float(dev.get("Humidity", 0))
                    sig = dev.get("SignalLevel", "N/A")
                    time = dev.get("LastUpdate", "Unknown")
                    dew = calc_dew_point(t, h)
                    
                    msg = (
                        f"🏠 **Данные с дачи**\n\n"
                        f"🌡 Температура: `{t}°C`\n"
                        f"💧 Влажность: `{h}%`\n"
                        f"🥤 Точка росы: `{dew}°C`\n"
                        f"📶 Сигнал: `{sig}/12`\n\n"
                        f"⏰ _Последний опрос: {time}_"
                    )
                    await message.answer(msg, parse_mode="Markdown")
                else:
                    await message.answer("⚠️ Не удалось получить данные от Domoticz.")
        except Exception as e:
            await message.answer(f"❌ Ошибка соединения: {e}")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())