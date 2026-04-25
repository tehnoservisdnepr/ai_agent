import feedparser
import requests
import json
import asyncio
import aiomqtt  # Чтобы слать данные Тому через MQTT
from ai_engine import get_ai_verdict

# --- НАСТРОЙКИ ---
MQTT_PARAMS = {"hostname": "192.168.0.166", "port": 1883}
TOPIC = "nii/v1/hunter/news"

async def fetch_and_hunt():
    URL = "https://hackaday.com/blog/feed/"
    print(f"📡 Сканирую {URL}...")
    feed = feedparser.parse(URL)
    
    async with aiomqtt.Client(**MQTT_PARAMS) as client:
        for entry in feed.entries[:3]: # Берем последние 3 новости
            print(f"\n📰 Новость: {entry.title}")
            
            # 1. Спрашиваем ИИ (Llama-3 через твой движок)
            analysis = await get_ai_verdict(entry.title)
            
            if isinstance(analysis, str):
                try: analysis = json.loads(analysis)
                except: analysis = {"ru_title": entry.title, "score": 0, "reason": "Error parsing"}

            # 2. Формируем пакет для Тома
            payload = {
                "hostname": "Hunter_Bot",
                "type": "news_analysis",
                "title": analysis.get('ru_title'),
                "score": analysis.get('score'),
                "reason": analysis.get('reason'),
                "link": entry.link
            }
            
            # 3. Пуляем в MQTT
            await client.publish(TOPIC, payload=json.dumps(payload))
            print(f"✅ Анализ отправлен Диспетчеру. Оценка: {analysis.get('score')}/10")

if __name__ == "__main__":
    asyncio.run(fetch_and_hunt())
    

