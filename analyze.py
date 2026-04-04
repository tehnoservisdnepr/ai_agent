#---------------------------
# Старт: 04.04.26
# Исправленная версия (Откат к рабочей логике)
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
        # Твой старый проверенный способ
        uv_sect = re.search(r'data-key=radiation.*?<div class="widget-row', html, re.S)
        uv_all = []
        if uv_sect:
            # Ищем все числа, окруженные тегами
            uv_all = [int(n) for n in re.findall(r'>\s*(\d+)\s*<', uv_sect.group(0))]

        # --- KP-ИНДЕКС ---
        # Берем блок геомагнитки
        kp_sect = re.search(r'data-key=geomagnetic.*?</div>\s*</div>', html, re.S)
        kp_all = []
        if kp_sect:
            # Вытаскиваем все одиночные цифры
            raw_nums = re.findall(r'\d+', kp_sect.group(0))
            # Фильтруем только индексы (длиной 1 символ), чтобы не схватить лишнего
            kp_all = [int(n) for n in raw_nums if len(n) == 1]
            # Meteofor может дублировать значения, берем первые 8 (на сутки)
            kp_all = kp_all[:8]

        # Определяем текущий индекс (шаг 3 часа)
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
        print(f"📊 Данные Meteofor:")
        print(f"☀️ УФ-индекс: {res['uv']} {res['uv_graph']}")
        print(f"🧲 Kp-индекс: {res['kp']} {res['kp_graph']}")