#---------------------------
# Стабильная версия: 04.04.26
# Исправлен поиск Kp-индекса
# v1.0 13:44 
#---------------------------

import requests
import re
from datetime import datetime

def get_weather_data():
    url = "https://www.meteofor.com.ua/weather-dnipro-5077/"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        html = response.text
        
        # УФ-индекс (поиск блока radiation)
        uv_sect = re.search(r'data-key="radiation".*?class="widget-row"', html, re.S)
        uv_all = [int(n) for n in re.findall(r'>\s*(\d+)\s*<', uv_sect.group(0))] if uv_sect else []

        # Kp-индекс (Геомагнитная активность)
        # Ищем блок geomagnetic и вытаскиваем цифры из ячеек
        kp_all = []
        kp_sect = re.search(r'data-key="geomagnetic".*?class="widget-row"', html, re.S)
        if kp_sect:
            # Ищем цифры в формате >5< или >0<
            kp_all = [int(n) for n in re.findall(r'>(\d)<', kp_sect.group(0))]

        # Индекс времени (каждые 3 часа)
        idx = datetime.now().hour // 3
        
        return {
            "uv": uv_all[idx] if idx < len(uv_all) else (uv_all[-1] if uv_all else 0),
            "kp": kp_all[idx] if idx < len(kp_all) else (kp_all[-1] if kp_all else 0),
            "uv_graph": uv_all,
            "kp_graph": kp_all
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    res = get_weather_data()
    if "error" in res:
        print(f"❌ Ошибка: {res['error']}")
    else:
        print(f"📊 Прогноз Meteofor:")
        print(f"☀️ УФ-индекс: {res['uv']} {res['uv_graph']}")
        print(f"🧲 Kp-индекс: {res['kp']} {res['kp_graph']}")