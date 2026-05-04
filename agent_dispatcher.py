import asyncio
import aiomqtt
import aiomysql
import json
import socket # Добавили для отлова сетевых ошибок

# --- КОНФИГУРАЦИЯ (без изменений) ---
MQTT_PARAMS = {
    "hostname": "192.168.0.166",
    "port": 1883,
    "timeout": 10 # Добавили таймаут, чтобы не висел вечно
}

DB_CONFIG = {
    'host': 'localhost',
    'user': 'tom',
    'password': 'tom',
    'db': 'nii_hub'
}

# ... (функции save_intelligence и update_node_and_metrics остаются без изменений) ...

async def mqtt_loop(db_pool):
    """Слушаем эфир НИИ с защитой от 'фиаско' при падении серверов"""
    broker = MQTT_PARAMS["hostname"]
    
    while True: # БЕСКОНЕЧНЫЙ ЦИКЛ ПЕРЕПОДКЛЮЧЕНИЯ
        try:
            print(f"📡 Попытка подключения к брокеру {broker}...")
            async with aiomqtt.Client(**MQTT_PARAMS) as client:
                await client.subscribe("nii/v1/#") 
                print(f"🚀 Агент Tom на связи. Слушаю nii/v1/#")
                
                async for message in client.messages:
                    try:
                        topic = str(message.topic)
                        payload = json.loads(message.payload.decode())

                        if "hunter" in topic:
                            await save_intelligence(db_pool, payload)
                            print(f"📰 Сохранена новость: {payload.get('title')[:40]}...")
                        
                        elif "tele" in topic:
                            await update_node_and_metrics(db_pool, payload)
                            print(f"✅ Метрики: {payload.get('hostname')}")

                    except json.JSONDecodeError:
                        print("⚠️ Ошибка JSON в полезной нагрузке")
                    except Exception as e:
                        print(f"❌ Ошибка обработки сообщения: {e}")

        except (aiomqtt.MqttError, socket.gaierror, OSError) as e:
            # Здесь ловим Errno 113 (No route to host) и прочие сетевые беды
            print(f"🔌 Потеряна связь с сервером {broker} ({e})")
            print("⏳ Ожидаю 60 секунд перед следующей попыткой...")
            await asyncio.sleep(60) # Не частим, пока чиним БП
        except Exception as e:
            print(f"🧨 Непредвиденная ошибка: {type(e).__name__}: {e}")
            await asyncio.sleep(10)

async def main():
    # Пул БД тоже может упасть, если MySQL не на этом же хосте, 
    # но пока считаем, что БД на локальной 'апельсинке' (localhost)
    async with aiomysql.create_pool(**DB_CONFIG) as pool:
        await mqtt_loop(pool)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Агент Tom ушел на перерыв.")
        