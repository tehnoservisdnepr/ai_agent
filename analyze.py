import asyncio
import aiohttp
import re
import mysql.connector
from datetime import datetime
from api_token import MYSQL_PASSWORD

async def get_weather_analysis():
    url = "https://www.meteofor.com.ua/ru/weather-dnipro-5077/"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
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

        # 2. УФ-ИНДЕКС (Вытягиваем все 8 значений суток)
        uv_all = []
        uv_sect = re.search(r'data-key=radiation.*?<div class="widget-row', html, re.S)
        if uv_sect:
            uv_all = [int(n) for n in re.findall(r'>\s*(\d+)\s*<', uv_sect.group(0))]

        # 3. KP-ИНДЕКС (Магнитные бури - все значения)
        kp_all = []
        start_index = html.find('data-key=geomagnetic')
        if start_index != -1:
            kp_block = html[start_index : start_index + 5000]
            # Ищем цифру в классе item-X
            kp_all = [int(n) for n in re.findall(r'class="[^"]*item-(\d)"', kp_block)]
        
        # Определяем текущий индекс (каждые 3 часа)
        idx = datetime.now().hour // 3
        
        # Формируем расширенный результат
        res = {
            "temp": temp,
            "uv_current": uv_all[idx] if idx < len(uv_all) else 0,
            "kp_current": kp_all[idx] if idx < len(kp_all) else 0,
            "uv_list": uv_all, # Весь список для графиков/динамики
            "kp_list": kp_all, # Весь список для графиков/динамики
            "max_uv": max(uv_all) if uv_all else 0,
            "max_kp": max(kp_all) if kp_all else 0
        }

        # --- ЗАПИСЬ В MYSQL ---
        try:
            conn = mysql.connector.connect(
                host='localhost',
                user='ai_worker',
                password=MYSQL_PASSWORD,
                database='nii_hub'
            )
            cursor = conn.cursor()
            # Пишем текущие значения в лог
            query = "INSERT INTO weather_log (temp, uv, kp, created_at) VALUES (%s, %s, %s, NOW())"
            cursor.execute(query, (res['temp'], res['uv_current'], res['kp_current']))
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
    if result:
        print(f"Текущая Т: {result['temp']}°C")
        print(f"УФ Динамика: {' -> '.join(map(str, result['uv_list']))}")
        print(f"КП Динамика: {' -> '.join(map(str, result['kp_list']))}")
Что тебе нужно сделать сейчас:
Замени содержимое analyze.py на этот код.

В основном файле бота (где формируется сообщение /status), поменяй вывод. Теперь у тебя есть res['uv_list'] и res['kp_list'].

Пример, как это можно вывести в Телеграм:

Python
uv_str = " -> ".join(map(str, weather['uv_list']))
kp_str = " -> ".join(map(str, weather['kp_list']))
msg = f"☀️ УФ (день): {uv_str}\n🧲 Kp (день): {kp_str}"


        
        
