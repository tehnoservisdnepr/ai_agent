import asyncio
import aiohttp
import re

async def dump():
    url = "https://www.meteofor.com.ua/ru/weather-dnipro-5077/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://www.google.com/"
    }
    
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url) as resp:
            html = await resp.text()
            
            # 1. Сохраним всё в файл, чтобы ты мог открыть его в Блокноте
            with open("raw_page.html", "w", encoding="utf-8") as f:
                f.write(html)
            
            print(f"Размер страницы: {len(html)} символов.")
            print("--- ИЩЕМ УПОМИНАНИЯ ТЕМПЕРАТУРЫ ---")
            
            # Находим все строки, где есть слово temperature и 20 символов вокруг
            matches = re.findall(r'.{0,30}temperature.{0,50}', html, re.IGNORECASE)
            for i, m in enumerate(matches[:10]): # выведем первые 10 находок
                print(f"{i+1}: {m}")

            # Проверим, есть ли вообще цифры со значком градуса
            degree_matches = re.findall(r'.{0,20}°C.{0,20}', html)
            print("\n--- ИЩЕМ ЗНАЧОК ГРАДУСА (°C) ---")
            if degree_matches:
                for d in degree_matches:
                    print(f"Найдено: {d}")
            else:
                print("Ни одного значка °C в коде не найдено!")

asyncio.run(dump())