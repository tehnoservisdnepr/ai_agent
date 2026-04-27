import asyncio
import json
from groq import AsyncGroq
from api_token import GROQ_API_KEY

# Инициализация асинхронного клиента
client = AsyncGroq(api_key=GROQ_API_KEY)

async def get_ai_verdict(title):
    try:
        # Вот здесь мы создаем ЗАПРОС (response) к нейросети
        response = await client.chat.completions.create(
            model="llama-3.3-70b-versatile",  # Ставим самую актуальную модель  model="llama-3.3-70b-versatile"
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Ты ассистент инженера Сергея. Он эксперт по инверторам, BMS, Linux и умным домам. "
                        "Проанализируй заголовок новости и ответь СТРОГО в формате JSON. "
                        "Поля: 'ru_title' (перевод на русский), 'score' (важность 1-10), 'reason' (почему это важно). "
                        "Приоритеты: солнечная энергетика, литиевые аккумуляторы, ESP32, Home Assistant. "
                        "Если новость не касается этих тем — ставь score ниже 3."
                    )
                },
                {"role": "user", "content": f"Новость: {title}"}
            ],
            response_format={"type": "json_object"}  # Гарантируем JSON на выходе
        )
        
        # Вытаскиваем текст ответа из объекта response
        verdict_text = response.choices[0].message.content
        return json.loads(verdict_text)
        
    except Exception as e:
        print(f"!!! Ошибка в ai_engine: {e}")
        return {
            "ru_title": "Ошибка анализа", 
            "score": 1, 
            "reason": f"Технический сбой: {str(e)}"
        }
        
        

