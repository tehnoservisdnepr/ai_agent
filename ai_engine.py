import asyncio
from groq import AsyncGroq  # КРИТИЧЕСКИ ВАЖНО: импортируем асинхронный клиент
from api_token import GROQ_API_KEY
from analyze import get_weather_analysis

# Инициализация асинхронного клиента
client = AsyncGroq(api_key=GROQ_API_KEY)

async def get_ai_verdict(network_status="OK"):
    weather = await get_weather_analysis()

    if not weather:
        return "❌ Не удалось получить данные для анализа."

    context = (
        f"Статус сети: {network_status}. "
        f"Температура: {weather['temp']}°C, "
        f"Магнитная активность (Kp): {weather['kp']}, "
        f"УФ-индекс: {weather['uv']}."
    )

    try:
# Используем актуальную модель Llama 3.1
        response = await client.chat.completions.create(
            model="llama-3.1-8b-instant", 
            messages=[
                {
                   "role": "system",
            "content": "Ты ведущий инженер-аналитик. Оценивай новости по шкале от 1 до 10. "
           "Твои главные интересы: Linux, промышленная автоматика, инверторы, "
           "солнечные панели (BMS, JK BMS), умный дом (Domoticz, Home Assistant) и Python. "
           "Если новость касается этих тем — ставь 8-10. Если это просто обзоры игр или ретро — ставь 1-3. "
           "Дай вердикт на русском языке кратко. НЕ используй символы * и _."
                },
                {"role": "user", "content": context}
            ]
        )
        verdict = response.choices[0].message.content
        
        # Очистка текста от спецсимволов Markdown, чтобы Telegram не ругался
        return verdict.replace("*", "").replace("_", "")
        
    except Exception as e:
        print(f"!!! Ошибка внутри ask_ai: {e}") # <-- Добавь эту строку
        return {"ru_title": "Ошибка анализа", "score": 1, "reason": str(e)}
        
        

