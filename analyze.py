import asyncio
import aiohttp
from datetime import datetime

async def get_weather_analysis():
    # Прямой адрес API для Днепра (ID 5077)
    api_url = "https://www.meteofor.com.ua/api/v1/weather/current/5077/"
    # Ссылка на страницу для парсинга индексов (они там еще есть в HTML)
    html_url = "https://www.meteofor.com.ua/ru/weather-dnipro-5077/"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "X-Requested-With": "XMLHttpRequest"
    }
    
    try:
        async with aiohttp.ClientSession(headers=headers) as session:
            # 1. Получаем температуру из API (чистый JSON)
            async with session.get(api_url) as resp:
                temp = "н/д"
                if resp.status == 200:
                    data = await resp.json()
                    temp = str(data.get('temperature', {}).get('c', 'н/д'))

            # 2. Получаем остальное из HTML (регулярки для индексов пока работают)
            async with session.get(html_url) as resp:
                html = await resp.text()

        # Поиск индексов (твой старый рабочий код)
        import re
        uv_sect = re.search(r'data-key=radiation.*?<div class="widget-row', html, re.S)
        uv_all = [int(n) for n in re.findall(r'>\s*(\d+)\s*<', uv_sect.group(0))] if uv_sect else []
        
        start_index = html.find('data-key=geomagnetic')
        kp_all = []
        if start_index != -1:
            kp_block = html[start_index : start_index + 5000]
            kp_all = [int(n) for n in re.findall(r'class="[^"]*item-(\d)"', kp_block)]
        
        kp_all = kp_all[:8]
        idx = datetime.now().hour // 3
        
        return {
            "temp": temp,
            "uv": uv_all[idx] if idx < len(uv_all) else (uv_all[-1] if uv_all else 0),
            "kp": kp_all[idx] if idx < len(kp_all) else (kp_all[-1] if kp_all else 0),
            "kp_graph": kp_all
        }
    except Exception as e:
        print(f"Ошибка: {e}")
        return None

if __name__ == "__main__":
    print(asyncio.run(get_weather_analysis()))


        
        