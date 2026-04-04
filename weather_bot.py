import asyncio
import logging
import aiohttp
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message

# Импортируем твою функцию анализа из соседнего файла analyze.py
from analyze import get_weather_analysis

# --- НАСТРОЙКИ ---
# Вставь сюда свой токен от BotFather
TOKEN = "8744550835:AAHb1VYtuMDqpJp6oyF8DUq-3plTMR1AZlk" 
# IP твоей дачи через NetBird
DOMOTICZ_URL = "http://100.96.33.208:8080/json.htm"

# Настройка логирования, чтобы видеть всё в консоли
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация
bot = Bot(token=TOKEN)
dp = Dispatcher()

# --- ФУНКЦИЯ ДЛЯ ДОМОТИКСА ---
async def get_domoticz_data():
    """Запрос данных с датчика idx 1 на даче"""
    params = {"type": "command", "param": "getdevices", "idx": "1"}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(DOMOTICZ_URL, params=params, timeout=5) as resp:
                if resp.status == 200:
                    return await resp.json()
    except Exception as e:
        logger.error(f"Ошибка Domoticz: {e}")
        return None

# --- ОБРАБОТЧИКИ КОМАНД ---

@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "🚀 **Система мониторинга запущена!**\n\n"
        "Используй /status для получения сводки по даче и внешним индексам (УФ/Магнитные бури)."
    )

@dp.message(Command("status"))
async def cmd_status(message: Message):
    # Запускаем запросы параллельно для скорости
    domo_task = asyncio.create_task(get_domoticz_data())
    weather_task = asyncio.create_task(get_weather_analysis())
    
    domo_data = await domo_task
    weather = await weather_task
    
    response = ["📊 **ТЕКУЩИЙ СТАТУС:**\n"]
    
    # 1. Данные с дачи
    if domo_data and "result" in domo_data:
        dev = domo_data["result"][0]
        temp = dev.get("Temp", "??")
        hum = dev.get("Humidity", "??")
        last = dev.get("LastUpdate", "??")
        response.append(f"🏠 **Дача (Днепр):**")
        response.append(f"🌡 Темп: `{temp}°C` | 💧 Влаж: `{hum}%`️")
        response.append(f"🕒 _Обновлено: {last}_")
    else:
        response.append("🏠 **Дача:** ⚠️ Оффлайн (нет связи)")

    response.append("\n" + "—" * 15 + "\n")


# 2. Данные из analyze.py (Meteofor)
    if weather:
        # Превращаем в числа, чтобы избежать ошибки TypeError
        try:
            kp = int(weather.get('kp', 0))
            uv = int(weather.get('uv', 0))
        except (ValueError, TypeError):
            kp = 0
            uv = 0
        
        # Теперь сравнение будет работать правильно
        kp_warn = "🔴 БУРЯ!" if kp >= 5 else "🟢 Спокойно"
        uv_warn = "⚠️ Нужна защита" if uv >= 6 else "✅ Безопасно"
        
        response.append(f"🌍 **Внешние индексы (Meteofor):**")
        response.append(f"🌡 По городу: `{weather.get('temp', 'н/д')}°C`")
        response.append(f"🧲 Магнитный (Kp): `{kp}` ({kp_warn})")
        response.append(f"☀️ УФ-индекс: `{uv}` ({uv_status if 'uv_status' in locals() else uv_warn})")
    else:
        response.append("🌍 **Внешние данные:** ⚠️ Ошибка парсинга")



    await message.answer("\n".join(response), parse_mode="Markdown")

# --- ЗАПУСК БОТА ---
async def main():
    # Очищаем все сообщения, которые пришли, пока бот был выключен
    await bot.delete_webhook(drop_pending_updates=True)
    logger.info("Бот запущен и готов к работе!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Бот остановлен.")