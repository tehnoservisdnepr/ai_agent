import aiohttp
import re
import logging

METEOFOR_URL = "https://meteofor.com.ua/weather-dnipro-4960/now/"

async def get_weather_analysis():
    """Парсинг Meteofor (УФ и Магнитные индексы) без bs4"""
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(METEOFOR_URL, timeout=10) as resp:
                if resp.status != 200: 
                    return None
                html = await resp.text()
                
                # Твои наработки по поиску индексов через регулярки
                uv_match = re.search(r'uv-index["\s>]+(\d+)', html)
                uv = uv_match.group(1) if uv_match else "0"
                
                kp_match = re.search(r'gm-index["\s>]+(\d+)', html) or re.search(r'(\d)\sбалл', html)
                kp = kp_match.group(1) if kp_match else "0"
                
                return {"uv": int(uv), "kp": int(kp)}
    except Exception as e:
        logging.error(f"Ошибка в analyze.py: {e}")
        return None