import asyncio
import aiohttp
import re
from datetime import datetime

async def get_weather_analysis():
    # Ссылка на Днепр
    url = "https://www.meteofor.com.ua/ru/weather-dnipro-5077/"
    
    # Максимально подробные заголовки, чтобы сайт думал, что зашел человек из Chrome
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Referer": "https://www.google.com/",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }
    
    try:
        # Используем сессию для поддержки cookies
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url, timeout=15) as response:
                if response.status != 200:
                    print(f"Ошибка доступа: статус {response.status}")
                    return None
                html = await response.text()

        temp = "н/д"
        
        # Ищем паттерн "temperatureAir":[число]
        # Мы видели это в твоем дампе: "temperatureAir":[10]
        t_match = re.search(r'"temperatureAir":\s?\[\s?(-?\d+)', html)
        
        if t_match:
            temp = t_match.group(1)
        else:
            # Запасной вариант, если ключ чуть другой (например, для ощущаемой)
            t_match = re.search(r'"temperature":\s?\{\s?"c":\s?(-?\d+)', html)
            if t_match:
                temp = t_match.group(1)

        # --- 2. ПОИСК УФ-ИНДЕКСА ---
        uv_all = []
        uv_sect = re.search(r'data-key=radiation.*?<div class="widget-row', html, re.S)
        if uv_sect:
            uv_all = [int(n) for n in re.findall(r'>\s*(\d+)\s*<', uv_sect.group(0))]

        # --- 3. ПОИСК KP-ИНДЕКСА (Магнитные бури) ---
        kp_all = []
        start_index = html.find('data-key=geomagnetic')
        if start_index != -1:
            kp_block = html[start_index : start_index + 5000]
            # Ищем классы item-1, item-2... это и есть уровни бури
            kp_all = [int(n) for n in re.findall(r'class="[^"]*item-(\d)"', kp_block)]
        
        # Ограничиваем список 8 значениями (на сутки)
        kp_all = kp_all[:8]
        
        # Определяем текущий индекс (каждые 3 часа)
        hour = datetime.now().hour
        idx = hour // 3
        
        return {
            "temp": temp,
            "uv": uv_all[idx] if idx < len(uv_all) else (uv_all[-1] if uv_all else 0),
            "kp": kp_all[idx] if idx < len(kp_all) else (kp_all[-1] if kp_all else 0),
            "uv_graph": uv_all[:8],
            "kp_graph": kp_all
        }

    except Exception as e:
        print(f"Ошибка в analyze.py: {e}")
        return None

# Для тестирования напрямую в консоли
if __name__ == "__main__":
    res = asyncio.run(get_weather_analysis())
    print("\n--- РЕЗУЛЬТАТ ТЕСТА ---")
    print(res)
    print("-----------------------\n")


        
        
