import asyncio
import aiohttp
import re
from datetime import datetime
from bs4 import BeautifulSoup

async def get_weather_analysis():
    url = "https://www.meteofor.com.ua/ru/weather-dnipro-5077/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url, timeout=15) as response:
                if response.status != 200:
                    return None
                html = await response.text()
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # --- ТЕМПЕРАТУРА ---
        # Сначала ищем по стандартному классу Meteofor
        temp_el = soup.find("span", class_="unit_temperature_c")
        if not temp_el:
            # Запасной вариант: ищем любой элемент, где в названии класса есть 'temperature'
            temp_el = soup.select_one('[class*="temperature"]')
        
        if temp_el:
            temp = temp_el.get_text(strip=True).replace('+', '').replace('°C', '')
        else:
            # Крайний случай: поиск через регулярку в тексте
            t_match = re.search(r'([+-]?\d+)\s*°C', html)
            temp = t_match.group(1).replace('+', '') if t_match else "н/д"

        # --- УФ-ИНДЕКС (Radiation) ---
        uv_sect = re.search(r'data-key=radiation.*?<div class="widget-row', html, re.S)
        uv_all = [int(n) for n in re.findall(r'>\s*(\d+)\s*<', uv_sect.group(0))] if uv_sect else []

        # --- KP-ИНДЕКС (Geomagnetic) ---
        kp_all = []
        start_index = html.find('data-key=geomagnetic')
        if start_index != -1:
            kp_block = html[start_index : start_index + 5000]
            # Ищем уровни активности (item-1, item-2 и т.д.)
            kp_all = [int(n) for n in re.findall(r'class="[^"]*item-(\d)"', kp_block)]
        
        kp_all = kp_all[:8] # Берем только 8 значений на текущие сутки
        idx = datetime.now().hour // 3
        
        return {
            "temp": temp,
            "uv": uv_all[idx] if idx < len(uv_all) else (uv_all[-1] if uv_all else 0),
            "kp": kp_all[idx] if idx < len(kp_all) else (kp_all[-1] if kp_all else 0),
            "kp_graph": kp_all
        }
    except Exception as e:
        print(f"Ошибка парсинга: {e}")
        return None

# Быстрый тест, если запустить файл напрямую
if __name__ == "__main__":
    res = asyncio.run(get_weather_analysis())
    print(f"\n--- ТЕСТ ПАРСЕРА ---\nРезультат: {res}\n--------------------")


        
        