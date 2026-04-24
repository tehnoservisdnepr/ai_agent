import asyncio
from ai_engine import get_ai_verdict

async def test():
    print("Запрос к Джарвису (через Groq)...")
    # Передаем текст новости прямо в функцию
    # (Убедись, что внутри get_ai_verdict переменная context берется правильно)
    result = await get_ai_verdict("Тестовая новость: Вышла новая прошивка для инверторов и JK BMS с поддержкой Linux")
    print(f"--- Готово! Вердикт ИИ: {result}")

if __name__ == "__main__":
    asyncio.run(test())