import asyncio
import aiomqtt
import aiomysql
import json

# --- КОНФИГУРАЦИЯ ---
MQTT_PARAMS = {
    "hostname": "192.168.0.166",
    "port": 1883
}

DB_CONFIG = {
    'host': 'localhost',
    'user': 'tom',
    'password': 'tom',
    'db': 'nii_hub'
}

async def save_intelligence(db_pool, data):
    """Записывает новости и аналитику от Hunter.py"""
    async with db_pool.acquire() as conn:
        async with conn.cursor() as cur:
            query = """
                INSERT INTO intelligence_feed 
                (agent_type, topic, title, summary, source_url) 
                VALUES (%s, %s, %s, %s, %s)
            """
            # Формируем заголовок с оценкой ИИ
            display_title = f"[{data.get('score', 0)}/10] {data.get('title')}"
            
            values = (
                "GROQ_ANALYST_V1", 
                "Electronics", 
                display_title, 
                data.get('reason'), 
                data.get('link')
            )
            await cur.execute(query, values)
            await conn.commit()

async def update_node_and_metrics(db_pool, data):
    """Твой старый добрый метод для апельсинок (без изменений)"""
    hostname = data.get('hostname', 'unknown_node')
    ip = data.get('ip', '0.0.0.0')
    temp = data.get('t', 0)
    load = data.get('l', 0)
    free_gb = data.get('f', 0)

    async with db_pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "INSERT INTO nodes (hostname, ip_netbird, status) VALUES (%s, %s, 'online') "
                "ON DUPLICATE KEY UPDATE ip_netbird=%s, status='online', last_seen=NOW()",
                (hostname, ip, ip)
            )
            await cur.execute("SELECT id FROM nodes WHERE hostname=%s", (hostname,))
            res = await cur.fetchone()
            if res:
                node_id = res[0]
                await cur.execute(
                    "INSERT INTO metrics (node_id, temp, cpu_load, ssd_free_gb) VALUES (%s, %s, %s, %s)",
                    (node_id, temp, load, free_gb)
                )
            # Пульс системы
            await cur.execute(
                "INSERT INTO system_health (component, status_message) "
                "VALUES ('dispatcher', 'OK') ON DUPLICATE KEY UPDATE last_pulse=NOW()",
            )
        await conn.commit()

async def mqtt_loop(db_pool):
    """Слушаем эфир НИИ (теперь и новости!)"""
    async with aiomqtt.Client(**MQTT_PARAMS) as client:
        # 1. ПОДПИСЫВАЕМСЯ НА ВСЁ в ветке nii/v1/
        await client.subscribe("nii/v1/#") 
        print("🚀 Агент Tom вышел на дежурство. Слушаю всё в nii/v1/#")
        
        async for message in client.messages:
            try:
                topic = str(message.topic)
                payload = json.loads(message.payload.decode())

                # 2. РАСПРЕДЕЛЯЕМ ПОТОКИ
                if "hunter" in topic:
                    await save_intelligence(db_pool, payload)
                    print(f"📰 Том сохранил новость: {payload.get('title')[:40]}...")
                
                elif "tele" in topic:
                    await update_node_and_metrics(db_pool, payload)
                    print(f"✅ Метрики обновлены: {payload.get('hostname')}")

            except Exception as e:
                print(f"❌ Ошибка обработки: {e}")

async def main():
    async with aiomysql.create_pool(**DB_CONFIG) as pool:
        await mqtt_loop(pool)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Агент Tom ушел на перерыв.")
        