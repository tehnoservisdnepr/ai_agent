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
                    "content": "Ты инженер-аналитик. Дай краткий вердикт. НЕ используй символы * и _."
                },
                {"role": "user", "content": context}
            ]
        )
        verdict = response.choices[0].message.content
        
        # Очистка текста от спецсимволов Markdown, чтобы Telegram не ругался
        return verdict.replace("*", "").replace("_", "")
        
    except Exception as e:
        return f"⚠️ Ошибка ИИ: {str(e)}"

