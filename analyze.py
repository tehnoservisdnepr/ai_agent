import asyncio
import aiohttp
import re
import mysql.connector
from datetime import datetime
# Импортируем тот самый пароль и ключи
from api_token import MYSQL_PASSWORD

async def get_weather_analysis():
    url = "https://www.meteofor.com.ua/ru/weather-dnipro-5077/"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Referer": "https://www.google.com/"
    }
    
    try:
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url, timeout=15) as response:
                if response.status != 200:
                    return None
                html = await response.text()

        # 1. ТЕМПЕРАТУРА
        temp = "н/д"
        t_match = re.search(r'"temperatureAir":\s?\[\s?(-?\d+)', html)
        if t_match:
            temp = t_match.group(1)

        # 2. УФ-ИНДЕКС
        uv_all = []
        uv_sect = re.search(r'data-key=radiation.*?<div class="widget-row', html, re.S)
        if uv_sect:
            uv_all = [int(n) for n in re.findall(r'>\s*(\d+)\s*<', uv_sect.group(0))]

        # 3. KP-ИНДЕКС (Магнитные бури)
        kp_all = []
        start_index = html.find('data-key=geomagnetic')
        if start_index != -1:
            kp_block = html[start_index : start_index + 5000]
            kp_all = [int(n) for n in re.findall(r'class="[^"]*item-(\d)"', kp_block)]
        
        idx = datetime.now().hour // 3
        
        res = {
            "temp": temp,
            "uv": uv_all[idx] if idx < len(uv_all) else 0,
            "kp": kp_all[idx] if idx < len(kp_all) else 0
        }

        # --- ЗАПИСЬ В ТВОЙ MYSQL ---
        try:
            conn = mysql.connector.connect(
                host='localhost',
                user='ai_worker', # Проверь имя пользователя базы
                password=MYSQL_PASSWORD,
                database='nii_hub'
            )
            cursor = conn.cursor()
            query = "INSERT INTO weather_log (temp, uv, kp, created_at) VALUES (%s, %s, %s, NOW())"
            cursor.execute(query, (res['temp'], res['uv'], res['kp']))
            conn.commit()
            cursor.close()
            conn.close()
        except Exception as db_e:
            print(f"Ошибка базы: {db_e}")

        return res

    except Exception as e:
        print(f"Ошибка в analyze.py: {e}")
        return None

if __name__ == "__main__":
    result = asyncio.run(get_weather_analysis())
    print(f"Результат: {result}")


        
        
