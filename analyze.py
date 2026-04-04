# Стабильная версия: 04.04.26
# Точка отсчета: data-row="geomagnetic"
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
        
        # --- УФ-ИНДЕКС ---
        uv_sect = re.search(r'data-key=radiation.*?<div class="widget-row', html, re.S)
        uv_all = [int(n) for n in re.findall(r'>\s*(\d+)\s*<', uv_sect.group(0))] if uv_sect else []

        # --- KP-ИНДЕКС (Ваша отправная точка) ---
        kp_all = []
        # Находим блок, который начинается с вашего ключевого слова
        # Ищем секцию от 'data-row="geomagnetic"' до следующего закрывающего блока виджета
        kp_sect = re.search(r'data-row=["\']?geomagnetic["\']?.*?</div>\s*</div>', html, re.S)
        
        if kp_sect:
            # Внутри этой секции ищем цифры в классах item-4, item-5 и т.д.
            # Это исключает попадание цифр из других таблиц
            kp_all = [int(n) for n in re.findall(r'class="item item-(\d)"', kp_sect.group(0))]
        
        # Если вдруг классы изменились, берем просто цифры внутри этой секции
        if not kp_all and kp_sect:
            kp_all = [int(n) for n in re.findall(r'>\s*(\d)\s*<', kp_sect.group(0))]

        # Ограничиваем прогноз на 8 значений (сутки)
        kp_all = kp_all[:8]

        # Индекс времени (3-часовой шаг)
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