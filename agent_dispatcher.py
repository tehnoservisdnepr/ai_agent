import asyncio
import aiomqtt
import aiomysql
import json

# Конфигурация (проверь IP своего брокера)
# Конфигурация (Том на 0.194 слушает брокера на 0.166)
MQTT_PARAMS = {
    "host": "192.168.0.166", # Исправил ключ на 'host'
    "port": 1883,
    "topic": "nii/v1/#"
}

DB_CONFIG = {
    'host': 'localhost',      # База здесь же, на 0.194
    'user': 'tom',
    'password': 'tom',
    'db': 'nii_hub'
}

async def update_node_and_metrics(db_pool, data):
    """Регистрирует апельсинку и записывает её здоровье"""
    hostname = data.get('hostname', 'unknown_node')
    ip = data.get('ip', '0.0.0.0')
    temp = data.get('t', 0)    # Температура
    load = data.get('l', 0)    # Нагрузка CPU
    free_gb = data.get('f', 0) # Свободно на SSD

    async with db_pool.acquire() as conn:
        async with conn.cursor() as cur:
            # 1. Авто-регистрация узла (nodes)
            await cur.execute(
                "INSERT INTO nodes (hostname, ip_netbird, status) VALUES (%s, %s, 'online') "
                "ON DUPLICATE KEY UPDATE ip_netbird=%s, status='online', last_seen=NOW()",
                (hostname, ip, ip)
            )
            
            # 2. Получаем внутренний ID узла
            await cur.execute("SELECT id FROM nodes WHERE hostname=%s", (hostname,))
            node_id = (await cur.fetchone())[0]
            
            # 3. Записываем метрики (metrics)
            await cur.execute(
                "INSERT INTO metrics (node_id, temp, cpu_load, ssd_free_gb) VALUES (%s, %s, %s, %s)",
                (node_id, temp, load, free_gb)
            )
            
            # 4. Отметка о работе самого Агента
            await cur.execute(
                "INSERT INTO system_health (component, status_message) "
                "VALUES ('dispatcher', 'OK') ON DUPLICATE KEY UPDATE last_pulse=NOW()",
            )
        await conn.commit()

async def mqtt_loop(db_pool):
    """Слушаем эфир НИИ"""
    async with aiomqtt.Client(**MQTT_PARAMS) as client:
        # Подписываемся на топик телеметрии
        await client.subscribe("nii/v1/+/tele") 
        print("🚀 Агент Tom вышел на дежурство. Слушаю MQTT...")
        
        async for message in client.messages:
            try:
                payload = json.loads(message.payload.decode())
                await update_node_and_metrics(db_pool, payload)
                print(f"✅ Обновлены данные от: {payload.get('hostname')}")
            except Exception as e:
                print(f"❌ Ошибка обработки: {e}")

async def main():
    # Создаем пул соединений с базой
    async with aiomysql.create_pool(**DB_CONFIG) as pool:
        await mqtt_loop(pool)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Агент Tom ушел на перерыв.")
        