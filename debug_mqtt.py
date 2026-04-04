#---------------------------
# старт 04.04.26
# 13:24
#
#---------------------------



import paho.mqtt.client as mqtt
import json
import time

# --- НАСТРОЙКИ ---
MQTT_HOST = "dacha"  # Или IP адрес
MQTT_PORT = 1883
TARGET_IDX = 1      # Укажите реальный IDX из вашего Domoticz!

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Подключено к брокеру!")
        # Подписываемся на выходной канал
        client.subscribe("domoticz/out")
        print("📡 Подписка на domoticz/out оформлена.")
        
        # Сразу отправляем запрос на получение данных
        payload = {"command": "getdeviceinfo", "idx": TARGET_IDX}
        client.publish("domoticz/in", json.dumps(payload))
        print(f"📤 Запрос для IDX {TARGET_IDX} отправлен в domoticz/in...")
    else:
        print(f"❌ Ошибка подключения. Код: {rc}")

def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        idx = data.get("idx")
        
        # Выводим вообще ВСЁ, что видим, чтобы понять, идет ли хоть какой-то поток
        print(f"📩 Сообщение в топике! IDX: {idx}, Название: {data.get('name')}")
        
        if idx == TARGET_IDX:
            print("\n🎯 ТОТ САМЫЙ ДАТЧИК!")
            print(f"Результат: {data.get('svalue1')}")
            print("-" * 30)
            
    except Exception as e:
        print(f"Ошибка разбора: {e}")

# Инициализация
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

print(f"🚀 Запуск отладки на {MQTT_HOST}...")
try:
    client.connect(MQTT_HOST, MQTT_PORT, 60)
    # Запускаем бесконечный цикл прослушки
    client.loop_forever()
except KeyboardInterrupt:
    print("\nОстановлено пользователем.")
except Exception as e:
    print(f"💥 Ошибка: {e}")