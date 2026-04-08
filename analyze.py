import aiohttp
import re
from datetime import datetime

async def get_weather_analysis():
    url = "https://www.meteofor.com.ua/ru/weather-dnipro-5077/"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    try:
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url, timeout=10) as response:
                if response.status != 200:
                    return None
                html = await response.text()
        
        # --- УФ-ИНДЕКС ---
        uv_sect = re.search(r'data-key=radiation.*?<div class="widget-row', html, re.S)
        uv_all = [int(n) for n in re.findall(r'>\s*(\d+)\s*<', uv_sect.group(0))] if uv_sect else []

        # --- KP-ИНДЕКС ---
        kp_all = []
        start_index = html.find('data-key=geomagnetic')
        if start_index != -1:
            kp_block = html[start_index : start_index + 5000]
            kp_all = [int(n) for n in re.findall(r'class="item item-(\d)"', kp_block)]
        
        kp_all = kp_all[:8]
        idx = datetime.now().hour // 3
        
        # --- ТЕМПЕРАТУРА (Универсальный поиск) ---
        # Ищем любое число (целое или с +/-), после которого стоит °C
        t_match = re.search(r'([+-]?\d+)\s*°C', html)
        
        if not t_match:
            # Запасной вариант по классу, если первый не сработал
            t_match = re.search(r'class="[^"]*unit_temperature_c[^"]*">([^<]+)', html)
            
        temp = t_match.group(1).replace('+', '').strip() if t_match else "н/д"
        
        return {
            "temp": temp,
            "uv": uv_all[idx] if idx < len(uv_all) else (uv_all[-1] if uv_all else 0),
            "kp": kp_all[idx] if idx < len(kp_all) else (kp_all[-1] if kp_all else 0),
            "kp_graph": kp_all
        }
    except Exception:
        return None


        
        