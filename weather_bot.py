import asyncio
import logging
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message

# Настройки
TOKEN = "8744550835:AA..." # Замени на свой полный токен
DOMOTICZ_URL = "http://100.96.33.208:8080/json.htm"
DEVICE_IDX = "1"

# Логирование (выводит всё в консоль)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=TOKEN)
dp = Dispatcher()

async def get_domoticz_data():
    """Получение данных с дачи через NetBird"""
    params = {
        "type": "command",
        "param": "getdevices",
        "idx": DEVICE_IDX
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(DOMOTICZ_URL, params=params, timeout=5) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"Ошибка Domoticz: статус {response.status}")
                    return None
    except Exception as e:
        logger.error(f"Ошибка подключения к 100.96.33.208: {e}")
        return None

@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("🚀 Бот запущен! Используй /status для проверки датчиков на даче.")

@dp.message(Command("status"))
async def cmd_status(message: Message):
    logger.info("Получена команда /status")
    await message.answer("⏳ Запрашиваю данные с узла 100.96.33.208...")
    
    data = await get_domoticz_data()
    
    if data and "result" in data:
        device = data["result"][0]
        temp = device.get("Temp", "Н/Д")
        hum = device.get("Humidity", "Н/Д")
        last_update = device.get("LastUpdate", "Неизвестно")
        
        text = (
            f"🏠 **Статус на даче:**\n"
            f"🌡 Температура: `{temp}°C`\n"
            f"💧 Влажность: `{hum}%`\n"
            f"🕒 Обновлено: {last_update}"
        )
        await message.answer(text, parse_mode="Markdown")
    else:
        await message.answer("❌ Не удалось получить данные. Проверь NetBird и Domoticz.")

# Эхо-хендлер для теста связи
@dp.message()
async def any_message(message: Message):
    logger.info(f"Сообщение от пользователя: {message.text}")
    await message.reply(f"Я слышу тебя! Ты написал: {message.text}. Попробуй /status")

async def main():
    logger.info("Запуск поллинга...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен")