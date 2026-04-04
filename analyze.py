#---------------------------
# Стабільна версія: 04.04.26
# Фікс: Хірургічний парсинг Kp по структурі row-item 
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
        uv_all = []
        uv_sect = re.search(r'data-key=["\']?radiation["\']?.*?class=["\']?widget-row["\']?', html, re.S)
        if uv_sect:
            uv_all = [int(n) for n in re.findall(r'>\s*(\d+)\s*<', uv_sect.group(0))]

        # --- KP-ІНДЕКС (Магнітні бурі) ---
        kp_all = []
        # 1. Знаходимо початок секції геомагнітної активності
        start_marker = html.find("Геомагнітна активність")
        if start_marker != -1:
            # 2. Беремо блок коду ПІСЛЯ заголовка (до наступного великого віджета)
            # 3000 символів зазвичай вистачає на всю таблицю індексів
            kp_area = html[start_marker:start_marker + 3000]
            
            # 3. Шукаємо цифри саме в структурі, яку ми побачили в дампі:
            # <div class="item item-4"> 4 </div>
            kp_all = [int(n) for n in re.findall(r'class="item item-\d">\s*(\d)\s*<', kp_area)]

        # Обрізаємо до 8 значень (прогноз на добу)
        kp_all = kp_all[:8]

        # Визначаємо поточний індекс за часом (крок 3 години)
        hour = datetime.now().hour
        idx = hour // 3
        
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