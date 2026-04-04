  
import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
import gmqtt  # Асинхронная библиотека MQTT

# --- НАСТРОЙКИ ---
TOKEN = "8744550835:AAHb1VYtuMDqpJp6oyF8DUq-3plTMR1AZlk"
MQTT_HOST = "dacha"  # IP вашей Raspberry Pi (или NetBird IP)
MQTT_PORT = 1883
MQTT_TOPIC = "domoticz/out"  # Топик, который слушаем

# Настройка логирования
logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)

# Инициализация бота
bot = Bot(token=TOKEN)
dp = Dispatcher()

# --- ХЕНДЛЕРЫ TELEGRAM ---

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(
        text="🔄 Обновить статус", callback_data="update_status")
    )
    await message.answer(
        f"🚀 Бот запущен на Windows!\nСлушаю MQTT на {MQTT_HOST}\nЖду данных...",
        reply_markup=builder.as_markup()
    )

@dp.callback_query(F.data == "update_status")
async def process_callback(callback: types.CallbackQuery):
    await callback.message.answer("Запрос статуса отправлен в MQTT...")
    # Здесь можно отправить команду в MQTT через client.publish
    await callback.answer()

@dp.message()
async def echo_handler(message: types.Message):
    """Ловит всё остальное, чтобы не было 'Update not handled'"""
    logger.info(f"Получено сообщение от {message.from_user.id}: {message.text}")
    await message.answer(f"Принято: {message.text}")

# --- ЛОГИКА MQTT (Асинхронная) ---

class MQTTClient:
    def __init__(self):
        self.client = gmqtt.Client("windows_spy_bot")

    def on_connect(self, client, flags, rc, properties):
        logger.info("✅ Подключено к MQTT брокеру!")
        self.client.subscribe(MQTT_TOPIC)

    def on_message(self, client, topic, payload, qos, properties):
        message_text = payload.decode()
        logger.info(f"📩 MQTT сообщение в {topic}: {message_text}")
        # Здесь можно добавить логику пересылки в Telegram конкретному пользователю
        # asyncio.create_task(bot.send_message(CHAT_ID, f"Данные: {message_text}"))

    async def connect(self):
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        await self.client.connect(MQTT_HOST, MQTT_PORT)

# --- ЗАПУСК ---

async def main():
    mqtt_client = MQTTClient()
    
    logger.info("🚀 Запуск асинхронных сервисов...")
    
    # Запускаем MQTT и Telegram параллельно
    try:
        await mqtt_client.connect()
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Ошибка при работе: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")