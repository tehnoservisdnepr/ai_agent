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
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
    }
    
    try:
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url, timeout=15) as response:
                if response.status != 200:
                    print(f"Ошибка доступа: статус {response.status}")
                    return None
                html = await response.text()

        # 1. ТЕМПЕРАТУРА
        temp = "н/д"
        t_match = re.search(r'"temperatureAir":\s?\[\s?(-?\d+)', html)
        if t_match:
            temp = t_match.group(1)

        # 2. УФ-ИНДЕКС (8 значений)
        uv_all = []
        uv_sect = re.search(r'data-key=radiation.*?<div class="widget-row', html, re.S)
        if uv_sect:
            uv_all = [int(n) for n in re.findall(r'>\s*(\d+)\s*<', uv_sect.group(0))]

        # 3. KP-ИНДЕКС (8 значений)
        kp_all = []
        start_index = html.find('data-key=geomagnetic')
        if start_index != -1:
            kp_block = html[start_index : start_index + 5000]
            kp_all = [int(n) for n in re.findall(r'class="[^"]*item-(\d)"', kp_block)]
        
        # Обрезаем списки до 8 значений (сутки)
        kp_all = kp_all[:8]
        uv_all = uv_all[:8]
        
        # Определяем индекс текущего времени (каждые 3 часа)
        idx = datetime.now().hour // 3
        
        # Формируем итоговый словарь для бота
        res = {
            "temp": temp,
            "uv_current": uv_all[idx] if idx < len(uv_all) else (uv_all[-1] if uv_all else 0),
            "kp_current": kp_all[idx] if idx < len(kp_all) else (kp_all[-1] if kp_all else 0),
            "uv_list": uv_all, # Для стрелочек в ТГ
            "kp_list": kp_all, # Для стрелочек в ТГ
            "max_uv": max(uv_all) if uv_all else 0,
            "max_kp": max(kp_all) if kp_all else 0
        }

        # --- ЗАПИСЬ В MYSQL (0.194) ---
        # Выполняем в отдельном потоке, чтобы не тормозить асинхронность
        def save_to_db():
            try:
                conn = mysql.connector.connect(
                    host='localhost',
                    user='ai_worker',
                    password=MYSQL_PASSWORD,
                    database='nii_hub',
                    connect_timeout=3
                )
                cursor = conn.cursor()
                
                # Исправили имена колонок на те, что реально есть в таблице:
                # temp, uv_current, kp_current, kp_list, uv_list, max_uv, max_kp
                query = """
                    INSERT INTO weather_log 
                    (temp, uv_current, kp_current, kp_list, uv_list, max_uv, max_kp) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                
                # Подготавливаем данные (конвертируем списки в текст)
                values = (
                    int(res['temp']), 
                    int(res['uv_current']), 
                    int(res['kp_current']),
                    str(res.get('kp_list', [])),
                    str(res.get('uv_list', [])),
                    int(res.get('max_uv', 0)),
                    int(res.get('max_kp', 0))
                )
                
                cursor.execute(query, values)
                conn.commit()
                
                print("✅ Данные успешно сохранены в БД!")
                
                cursor.close()
                conn.close()
            except Exception as db_e:
                print(f"❌ Ошибка БД на 0.194: {db_e}")

        # Запускаем фоном
        asyncio.create_task(asyncio.to_thread(save_to_db))

        return res

    except Exception as e:
        print(f"Ошибка в analyze.py: {e}")
        return None

# Тест
if __name__ == "__main__":
    result = asyncio.run(get_weather_analysis())
    print(result)


        
        
