import asyncio
import json
import paho.mqtt.client as mqtt
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from analyze import get_weather_analysis

# --- КОНФИГУРАЦИЯ ---
API_TOKEN = '8744550835:AAHb1VYtuMDqpJp6oyF8DUq-3plTMR1AZlk'
ALLOWED_USERS = [887949813,742097442]  # Вставьте вместо ID_СЫНА его цифры
#   ADMIN_ID = 887949813
MQTT_BROKER = "192.168.0.123"
MQTT_TOPIC = "domoticz/in"

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Функция отправки в Domoticz
def send_to_domoticz(res):
    try:
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        client.connect(MQTT_BROKER, 1883, 30)
        
        payloads = [
            {"command": "udevice", "idx": 14, "nvalue": 0, "svalue": str(res['temp'])},
            {"command": "udevice", "idx": 15, "nvalue": 0, "svalue": f"{res['uv']};0"},
            {"command": "udevice", "idx": 16, "nvalue": 0, "svalue": str(res['kp'])}
        ]
        
        for p in payloads:
            client.publish(MQTT_TOPIC, json.dumps(p))
        client.disconnect()
        return "✅ Данные на Дачу доставлены"
    except Exception as e:
        return f"⚠️ Ошибка MQTT: {e}"




@dp.message(Command("status"))
async def cmd_status(message: types.Message):
    if message.from_user.id not in ALLOWED_USERS: return
    #if message.from_user.id != ADMIN_ID: return

    wait_msg = await message.answer("🔄 Запрашиваю данные...")
    res = await get_weather_analysis()
    
    if res:
        mqtt_status = send_to_domoticz(res)
        
        
        # Добавьте эти строки перед формированием переменной text
        uv_warning = "⚠️ Высокий!" if float(res['uv']) >= 6 else "✅ Норма"
        kp_warning = "🆘 БУРЯ!" if float(res['kp']) >= 5 else ""

        text = (
            f"📊 **ТЕКУЩИЙ СТАТУС:**\n\n"
            f"🏠 Дача: {mqtt_status}\n"
            f"———————————————\n"
            f"🌍 Днепр (Meteofor):\n"
            f"🌡 Температура: {res['temp']}°C\n"
            f"🧲 Kp-индекс: {res['kp']} {kp_warning}\n"
            f"☀️ УФ-индекс: {res['uv']} ({uv_warning})\n"
            f"📈 Прогноз Kp: {', '.join(map(str, res['kp_graph']))}\n\n"
            f"🧐 _Помни: данные из аэропорта, верь своим чувствам!_"
        )
    
    else:
        text = "❌ Ошибка получения данных с Meteofor"
    
    await wait_msg.edit_text(text, parse_mode="Markdown")

async def main():
    print("🚀 Бот-дежурный запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())