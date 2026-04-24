import feedparser
import mysql.connector
import requests
import json
import sys
from ai_engine import get_ai_verdict
import asyncio


# Настройка вывода для терминала
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# --- НАСТРОЙКИ ---
API_KEY = "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" 
DB_CONFIG = {
    "host": "localhost",
    "user": "tom",
    "password": "123456",
    "database": "ai_agents"
}

    
def ask_ai(title):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    prompt = f"Ты помощник инженера Сергея. Он чинит инверторы и BMS. Проанализируй новость: '{title}'. 1. Переведи на русский. 2. Оцени полезность для мастера электроники (0-10). Ответь ТОЛЬКО чистым JSON: {{\"ru_title\": \"...\", \"score\": 0, \"reason\": \"...\"}}"
    
    

    
    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": prompt}],
        "response_format": {"type": "json_object"} # Groq умеет гарантировать JSON!
    }
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data), timeout=15)
        res_json = response.json()
        content = res_json['choices'][0]['message']['content']
        return json.loads(content)
    except Exception as e:
        return {"ru_title": f"Ошибка анализа", "score": 1, "reason": str(e)}

def save_to_db(ru_title, score, reason, link):
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        query = "INSERT INTO intelligence_feed (agent_type, topic, title, summary, source_url) VALUES (%s, %s, %s, %s, %s)"
        display_title = f"[{score}/10] {ru_title}"
        values = ("GROQ_ANALYST_V1", "Electronics", display_title, reason, link)
        cursor.execute(query, values)
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Ошибка БД: {e}")
        return False

async def fetch_news():  # Добавили async
    URL = "https://hackaday.com/blog/feed/"
    print(f"Сканирую {URL}...")
    feed = feedparser.parse(URL)
    
    for entry in feed.entries[:3]:
        print(f"\nНовость: {entry.title}")
        print(f"  --> Джарвис (через Groq) анализирует...")
        analysis = await get_ai_verdict(entry.title)
        # Если пришла строка, пробуем превратить её в словарь
        if isinstance(analysis, str):
            try:
                import json
                analysis = json.loads(analysis)
            except:
                # Если совсем всё плохо, создаем "заглушку"
                analysis = {"ru_title": analysis, "score": 1, "reason": "Не удалось распарсить JSON"}
        if save_to_db(analysis['ru_title'], analysis['score'], analysis['reason'], entry.link):
            print(f"--- Готово! Оценка ИИ: {analysis['score']}/10")

if __name__ == "__main__":
    asyncio.run(fetch_news())

