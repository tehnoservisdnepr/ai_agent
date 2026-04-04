#---------------------------
# старт 04.04.26
# 13:24
#   
#---------------------------

import requests
import re
from datetime import datetime
##################################################
def get_weather_data():
    url = "https://www.meteofor.com.ua/weather-dnipro-5077/"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        html = response.text
        
        # УФ
        uv_sect = re.search(r'data-key=radiation.*?<div class="widget-row', html, re.S)
        uv_all = [int(n) for n in re.findall(r'>\s*(\d+)\s*<', uv_sect.group(0))] if uv_sect else []

        # Kp
        kp_sect = re.search(r'data-key=geomagnetic.*?</div>\s*</div>', html, re.S)
        kp_all = []
        if kp_sect:
            raw_nums = re.findall(r'\d+', kp_sect.group(0))
            temp_kp = [int(n) for n in raw_nums if len(n) == 1]
            for x in temp_kp:
                if (not kp_all or kp_all[-1] != x or len(kp_all) < 8) and len(kp_all) < 8:
                    kp_all.append(x)

        idx = datetime.now().hour // 3
        return {
            "uv": uv_all[idx] if idx < len(uv_all) else (uv_all[-1] if uv_all else 0),
            "kp": kp_all[idx] if idx < len(kp_all) else (kp_all[-1] if kp_all else 0),
            "uv_graph": uv_all,
            "kp_graph": kp_all
        }
    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    res = get_weather_data()
    print(f"УФ: {res['uv']} {res['uv_graph']}")
    print(f"Kp: {res['kp']} {res['kp_graph']}")