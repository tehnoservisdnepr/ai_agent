import asyncio
from groq import AsyncGroq  # КРИТИЧЕСКИ ВАЖНО: импортируем асинхронный клиент
from api_token import GROQ_API_KEY
from analyze import get_weather_analysis
import json

# Инициализация асинхронного клиента
client = AsyncGroq(api_key=GROQ_API_KEY)

async def get_ai_verdict(title): # Теперь принимаем заголовок новости
    try:
        response = await client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Ты ассистент инженера Сергея. Он эксперт по инверторам, BMS, Linux и умным домам. "
                        "Проанализируй заголовок новости и ответь СТРОГО в формате JSON. "
                        "Поля: 'ru_title' (перевод), 'score' (число 1-10), 'reason' (кратко почему). "
                        "Интересы: электроника, солнечная энергетика, автоматизация. "
                        "Если тема — ретро-игры, ставь score 1-3."
                    )
                },
                {"role": "user", "content": f"Новость: {title}"}
            ],
            response_format={"type": "json_object"} # Заставляем Groq выдать JSON
        )
        
        verdict_text = response.choices[0].message.content
        # Превращаем текст в настоящий словарь Python
        return json.loads(verdict_text)
        
    except Exception as e:
        print(f"!!! Ошибка внутри get_ai_verdict: {e}")
        return {"ru_title": "Ошибка анализа", "score": 1, "reason": str(e)}
        
        

