import asyncio
import json
import paho.mqtt.client as mqtt
from analyze import get_weather_analysis

# --- НАСТРОЙКИ ---
MQTT_BROKER = "192.168.0.198"
MQTT_TOPIC = "domoticz/in"

async def run_update():
    print("[*] Запуск обновления...")
    res = await get_weather_analysis()
    
    if not res:
        print("[!] Ошибка: Парсер не вернул данных.")
        return

    print(f"[*] Данные получены: Temp={res['temp']}, UV={res['uv']}, Kp={res['kp']}")

    try:
        # ВАЖНО: для paho-mqtt 2.1.0 указываем CallbackAPIVersion
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        
        print(f"[*] Подключение к брокеру {MQTT_BROKER}...")
        client.connect(MQTT_BROKER, 1883, 60)
        
        # Список датчиков для отправки
        payloads = [
            {"command": "udevice", "idx": 14, "nvalue": 0, "svalue": str(res['temp'])},
            {"command": "udevice", "idx": 15, "nvalue": 0, "svalue": f"{res['uv']};0"},
            {"command": "udevice", "idx": 16, "nvalue": 0, "svalue": str(res['kp'])}
        ]

        for p in payloads:
            client.publish(MQTT_TOPIC, json.dumps(p))
            print(f"[OK] Отправлен IDX {p['idx']}")

        client.disconnect()
        print("[*] Все данные успешно переданы в Domoticz.")

    except Exception as e:
        print(f"[!] Ошибка MQTT: {e}")

if __name__ == "__main__":
    asyncio.run(run_update())