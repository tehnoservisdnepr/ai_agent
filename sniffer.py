import paho.mqtt.client as mqtt

# Твой IP из NetBird
MQTT_HOST = "100.96.33.208"

def on_message(client, userdata, message):
    # Печатаем ТОПИК и само СООБЩЕНИЕ
    print(f"📡 Топик: {message.topic} \n📩 Данные: {message.payload.decode()}\n" + "-"*30)

client = mqtt.Client()
client.on_message = on_message

print(f"🔍 Подключаюсь к {MQTT_HOST} и слушаю эфир...")
client.connect(MQTT_HOST, 1883, 60)
client.subscribe("#") # Решетка значит "слушать всё"

client.loop_forever()