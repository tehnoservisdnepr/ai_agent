import asyncio
import logging
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message

# --- НАСТРОЙКИ ---
TOKEN = "8744550835:AAHb1VYtuMDqpJp6oyF8DUq-3plTMR1AZlk" 
DOMOTICZ_URL = "http://100.96.33.208:8080/json.htm"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=TOKEN)
dp = Dispatcher()

async def get_domoticz_devices():
    params = {"type": "command", "param": "getdevices"}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(DOMOTICZ_URL, params=params, timeout=5) as resp:
                if resp.status == 200:
                    return await resp.json()
    except Exception as e:
        logger.error(f"Ошибка запроса: {e}")
    return None

@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("✅ Бот на связи!\n/status — Температура на даче\n/all — Все датчики")

@dp.message(Command("status"))
async def cmd_status(message: Message):
    data = await get_domoticz_devices()
    if not data or "result" not in data:
        return await message.answer("❌ Ошибка получения данных.")

    # Ищем устройство с idx 1
    device = next((item for item in data["result"] if item["idx"] == "1"), None)
    
    if device:
        temp = device.get("Temp", "??")
        hum = device.get("Humidity", "??")
        last = device.get("LastUpdate", "??")
        text = (f"🌡 **Температура:** `{temp}°C`\n"
                f"💧 **Влажность:** `{hum}%`\n"
                f"🕒 **Обновлено:** `{last}`")
        await message.answer(text, parse_mode="Markdown")
    else:
        await message.answer("❓ Датчик с idx 1 не найден.")

@dp.message(Command("all"))
async def cmd_all(message: Message):
    data = await get_domoticz_devices()
    if not data or "result" not in data:
        return await message.answer("❌ Ошибка.")

    lines = ["📊 **Текущие показатели:**"]
    for dev in data["result"]:
        name = dev.get("Name", "Без имени")
        val = dev.get("Data", "Нет данных")
        lines.append(f"🔹 **{name}**: `{val}`")
    
    await message.answer("\n".join(lines), parse_mode="Markdown")

async def main():
    # Удаляем старые сообщения, чтобы бот не захлебнулся при старте
    await bot.delete_webhook(drop_pending_updates=True)
    logger.info("Бот запущен и очистил очередь сообщений...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())