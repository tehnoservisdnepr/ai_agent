#---------------------------
# Стабильная версия: 04.04.26
# Исправлено разделение Temp;Hum
# v1.0 13:45
#---------------------------

import paho.mqtt.client as mqtt
import json
import time

# --- НАСТРОЙКИ ---
MQTT_HOST = "dacha" 
MQTT_PORT = 1883
TARGET_IDX = 1  # Ваш реальный датчик ESP8266

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Подключено к брокеру!")
        client.subscribe("domoticz/out")
        print("📡 Подписка на domoticz/out оформлена.")
        
        # Запрос данных
        payload = {"command": "getdeviceinfo", "idx": TARGET_IDX}
        client.publish("domoticz/in", json.dumps(payload))
        print(f"📤 Запрос состояния IDX {TARGET_IDX} отправлен...")
    else:
        print(f"❌ Ошибка подключения: {rc}")

def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        if data.get("idx") == TARGET_IDX:
            print("\n🎯 ДАННЫЕ С ДАЧИ ПОЛУЧЕНЫ:")
            print(f"Название: {data.get('name')}")
            
            svalue = data.get("svalue1", "")
            if ";" in svalue:
                # Разделяем: Температура;Влажность;Прочее
                parts = svalue.split(";")
                temp = parts[0]
                hum = parts[1]
                print(f"🌡 Температура: {temp}°C")
                print(f"💧 Влажность: {hum}%")
            else:
                print(f"Значение: {svalue}")
            print("-" * 30)
            
    except Exception as e:
        print(f"❌ Ошибка разбора JSON: {e}")

# Использование актуальной версии API (убирает DeprecationWarning)
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
client.on_connect = on_connect
client.on_message = on_message

print(f"🚀 Запуск мониторинга на {MQTT_HOST}...")
try:
    client.connect(MQTT_HOST, MQTT_PORT, 60)
    client.loop_forever()
except KeyboardInterrupt:
    print("\n👋 Остановлено пользователем.")
except Exception as e:
    print(f"💥 Ошибка: {e}")