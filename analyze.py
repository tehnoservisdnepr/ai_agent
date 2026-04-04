##---------------------------
# Стабільна версія: 04.04.26
# Фікс: Прямий збір Kp з класів item-X
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
        
        # --- УФ-ІНДЕКС ---
        uv_sect = re.search(r'data-key=radiation.*?<div class="widget-row', html, re.S)
        uv_all = [int(n) for n in re.findall(r'>\s*(\d+)\s*<', uv_sect.group(0))] if uv_sect else []

        # --- KP-ІНДЕКС ---
        # Витягуємо цифру прямо з назви класу (наприклад, item-5 -> 5)
        # Це той самий метод, який відповідає вашому дампу
        kp_all = [int(n) for n in re.findall(r'class="item item-(\d)"', html)]
        
        # Meteofor зазвичай видає 8 значень на добу
        kp_all = kp_all[:8]

        # Визначаємо індекс за поточним часом (крок 3 години)
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
    if isinstance(res, dict) and "error" not in res:
        print(f"📊 Сводка Meteofor (Дніпро):")
        print(f"☀️ УФ: {res['uv']} {res['uv_graph']}")
        print(f"🧲 Kp: {res['kp']} {res['kp_graph']}")
    else:
        print(f"❌ Помилка: {res}")