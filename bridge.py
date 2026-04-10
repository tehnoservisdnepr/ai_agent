import asyncio
import json
import paho.mqtt.client as mqtt
from analyze import get_weather_analysis

# --- НАСТРОЙКИ ---
MQTT_BROKER = "192.168.0.198" 
MQTT_TOPIC = "domoticz/in"

def publish_to_domoticz(idx, svalue):
    client = mqtt.Client()
    try:
        client.connect(MQTT_BROKER, 1883, 60)
        payload = {
            "command": "udevice",
            "idx": idx,
            "nvalue": 0,
            "svalue": str(svalue)
        }
        client.publish(MQTT_TOPIC, json.dumps(payload))
        client.disconnect()
        print(f" [OK] Отправлено IDX {idx}: {svalue}")
    except Exception as e:
        print(f" [ERR] Ошибка MQTT для IDX {idx}: {e}")

async def main():
    print("--- Запуск обновления данных для Дачи ---")
    data = await get_weather_analysis()
    
    if data:
        # Температура
        publish_to_domoticz(14, data['temp'])
        # УФ-индекс
        publish_to_domoticz(15, f"{data['uv']};0")
        # Kp-индекс
        publish_to_domoticz(16, data['kp'])
        print("--- Обновление завершено успешно ---")
    else:
        print("!!! Не удалось получить данные из парсера")

if __name__ == "__main__":
    asyncio.run(main())