#---------------------------
# Старт: 04.04.26
# Фикс: Захват всей последовательности Kp (8 значений)
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
        
        # --- УФ-ИНДЕКС (Стабильно) ---
        uv_sect = re.search(r'data-key=radiation.*?<div class="widget-row', html, re.S)
        uv_all = [int(n) for n in re.findall(r'>\s*(\d+)\s*<', uv_sect.group(0))] if uv_sect else []

        # --- KP-ИНДЕКС (Полная последовательность) ---
        kp_all = []
        # Находим начало блока геомагнитки
        start_index = html.find('data-key=geomagnetic')
        if start_index != -1:
            # Берем кусок кода с запасом (например, 5000 символов), 
            # где гарантированно лежат все 8 плашек row-item
            kp_block = html[start_index : start_index + 5000]
            
            # Ищем ВСЕ цифры в классах item-X внутри этого блока
            kp_all = [int(n) for n in re.findall(r'class="item item-(\d)"', kp_block)]
        
        # Оставляем только первые 8 (прогноз на ближайшие 24 часа)
        kp_all = kp_all[:8]

        # Определяем индекс по текущему времени (3-часовой шаг)
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
    print(f"📊 Сводка Meteofor (Днепр):")
    print(f"☀️ УФ: {res.get('uv')} {res.get('uv_graph')}")
    print(f"🧲 Kp: {res.get('kp')} {res.get('kp_graph')}")