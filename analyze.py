import aiohttp
import re
import logging

# URL строго по твоему скриншоту
METEOFOR_URL = "https://meteofor.com.ua/ru/weather-dnipro-5077/"

async def get_weather_analysis():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
    }
    try:
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(METEOFOR_URL, timeout=10) as resp:
                if resp.status != 200:
                    return None
                html = await resp.text()

                # 1. Температура (ищем цифру перед °C)
                t_match = re.search(r'(\+?\d+)°C', html)
                temp = t_match.group(1).replace('+', '') if t_match else "14"

                # 2. Kp-индекс (Геомагнитная активность)
                # Ищем ВСЕ цифры в блоках gm-index и берем МАКСИМАЛЬНУЮ на сегодня
                kp_vals = re.findall(r'gm-index.*?(\d+)', html, re.S)
                kp = max([int(x) for x in kp_vals]) if kp_vals else 0

                # 3. УФ-индекс (аналогично — максимум)
                uv_vals = re.findall(r'uv-index.*?(\d+)', html, re.S)
                uv = max([int(x) for x in uv_vals]) if uv_vals else 0

                return {
                    "temp": temp,
                    "uv": uv,
                    "kp": kp
                }
    except Exception as e:
        logging.error(f"Ошибка парсинга: {e}")
        return None


        
        