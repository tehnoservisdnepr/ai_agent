import paho.mqtt.client as mqtt
import json
import math
from datetime import datetime

MQTT_HOST = "100.96.33.208"
MQTT_PORT = 1883
TARGET_IDX = 1

def calculate_dew_point(T, Rh):
    # Коэффициенты для формулы Магнуса (стандарт для метео)
    b, c = 17.625, 243.04
    gamma = math.log(Rh/100) + (b * T) / (c + T)
    return (c * gamma) / (b - gamma)

def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        
        if data.get("idx") == TARGET_IDX:
            T = float(data.get("svalue1", 0))
            Rh = float(data.get("svalue2", 0))
            dew_point = calculate_dew_point(T, Rh)
            
            print(f"\n✅ ДАННЫЕ С ДАЧИ (IDX: {TARGET_IDX})")
            print(f"🌡 Температура: {T}°C")
            print(f"💧 Влажность:   {Rh}%")
            print(f"🥤 Точка росы:  {dew_point:.2f}°C") # Наш "Компот"
            
            # Статус комфорта (как в Domoticz)
            status = "Нормально" if 40 <= Rh <= 60 else "Сухо/Влажно"
            print(f"✨ Статус:      {status}")
            print(f"🕒 Обновлено:   {data.get('LastUpdate')}")
            print("-" * 35)
            
    except Exception as e:
        pass # Игнорируем системный шум

client = mqtt.Client()
client.on_message = on_message

try:
    client.connect(MQTT_HOST, MQTT_PORT, 60)
    client.subscribe("domoticz/out")
    # Принудительный запрос статуса
    client.publish("domoticz/in", json.dumps({"command": "getdeviceinfo", "idx": TARGET_IDX}))
    print(f"🚀 Мониторинг {MQTT_HOST} запущен...")
    client.loop_forever()
except Exception as e:
    print(f"❌ Сбой: {e}")