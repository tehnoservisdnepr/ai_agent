import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from datetime import datetime

# Импортируем твой исправленный парсер
from analyze import get_weather_analysis

# --- НАСТРОЙКИ ---
API_TOKEN = '8744550835:AAHb1VYtuMDqpJp6oyF8DUq-3plTMR1AZlk'  # Вставь свой токен
ADMIN_ID = 8744550835        # Вставь свой числовой ID (был в логах)

# Настройка логирования, чтобы в консоли было видно, что происходит
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%H:%M:%S"
)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# --- ФУНКЦИИ ИНТЕРФЕЙСА ---

async def set_main_menu(bot: Bot):
    """Создает синюю кнопку 'Меню' слева от поля ввода"""
    main_menu_commands = [
        types.BotCommand(command="/status", description="📊 Текущий статус"),
        types.BotCommand(command="/start", description="🔄 Перезапуск"),
        types.BotCommand(command="/help", description="❓ Помощь")
    ]
    await bot.set_my_commands(main_menu_commands)

async def on_startup(dispatcher):
    """Выполняется один раз при запуске скрипта"""
    await set_main_menu(bot)
    try:
        await bot.send_message(ADMIN_ID, "🚀 **Бот запущен и готов к работе!**\nПарсер Meteofor: ✅ OK\nДанные: Актуальны")
        logging.info("Бот успешно отправил уведомление о запуске.")
    except Exception as e:
        logging.error(f"Не удалось отправить уведомление админу: {e}")

# --- ОБРАБОТЧИКИ КОМАНД ---

@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    await message.reply(
        "👋 Привет! Я бот-монитор.\n\n"
        "Жми **/status**, чтобы узнать погоду в Днепре и состояние датчиков."
    )

@dp.message_handler(commands=['status'])
async def status_command(message: types.Message):
    # Показываем "печатает...", пока скрипт парсит сайт
    await bot.send_chat_action(message.chat.id, types.ChatActions.TYPING)
    
    res = await get_weather_analysis()
    
    if not res:
        await message.answer("❌ Ошибка при получении данных.")
        return

    # Формируем текст сообщения
    text = (
        f"📊 **ТЕКУЩИЙ СТАТУС:**\n\n"
        f"🏠 Дача: ⚠️ Оффлайн\n"
        f"———————————————\n\n"
        f"🌍 **Внешние данные (Днепр):**\n"
        f"🌡 По городу: {res['temp']}°C\n"
        f"🧲 Kp: {res['kp']} ({'🟢 Спокойно' if res['kp'] < 4 else '🔴 Буря!'})\n"
        f"☀️ УФ: {res['uv']} ({'🟢 Низкий' if res['uv'] < 3 else '⚠️ Нужна защита'})\n"
        f"📊 Прогноз Kp: {res['kp_graph']}"
    )
    
    await message.answer(text, parse_mode="Markdown")

# --- ЗАПУСК ---

if __name__ == "__main__":
    # skip_updates=True игнорирует сообщения, присланные пока бот был выключен
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)