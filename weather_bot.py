import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.enums import ChatAction

# Твой рабочий парсер
from analyze import get_weather_analysis

#8744550835:AAHb1VYtuMDqpJp6oyF8DUq-3plTMR1AZlk
#8744550835
# --- ДАННЫЕ (БЕЗ ШПИОНОМАНИИ) ---
API_TOKEN = '8744550835:AAHb1VYtuMDqpJp6oyF8DUq-3plTMR1AZlk'  # Вставь свой токен
ADMIN_ID = 8744550835  # Вставь свой реальный ID, который на "8"
# breakpoint()

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# --- МЕНЮ ---

async def set_main_menu():
    main_menu_commands = [
        types.BotCommand(command="status", description="📊 Проверить статус"),
        types.BotCommand(command="start", description="🔄 Старт"),
    ]
    await bot.set_my_commands(main_menu_commands)

# --- ОБРАБОТЧИКИ ---

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    # Если хочешь точно узнать свой ID, раскомментируй строку ниже:
    # print(f"Твой ID: {message.from_user.id}")
    await message.answer("👋 Привет! Я готов. Жми /status")

@dp.message(Command("status"))
async def cmd_status(message: types.Message):
    await bot.send_chat_action(message.chat.id, ChatAction.TYPING)
    res = await get_weather_analysis()
    
    if not res:
        await message.answer("❌ Ошибка получения данных.")
        return

    text = (
        f"📊 **ТЕКУЩИЙ СТАТУС:**\n\n"
        f"🏠 Дача: ⚠️ Оффлайн\n"
        f"———————————————\n\n"
        f"🌍 **Внешние данные (Днепр):**\n"
        f"🌡 По городу: {res['temp']}°C\n"
        f"🧲 Kp-индекс: {res['kp']} ({'🟢 Ок' if res['kp'] < 4 else '🔴 Буря'})\n"
        f"☀️ УФ-индекс: {res['uv']} ({'🟢 Ок' if res['uv'] < 3 else '⚠️ Опасно'})\n"
        f"📊 Прогноз Kp: {res['kp_graph']}"
    )
    await message.answer(text, parse_mode="Markdown")

# --- ЗАПУСК ---

async def main():
    await set_main_menu()
    try:
        await bot.send_message(ADMIN_ID, "🚀 **Бот запущен!**\nID на 8 подтвержден.")
    except Exception as e:
        print(f"Уведомление не ушло: {e}")
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Бот выключен")