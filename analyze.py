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
                    print(f"РћС€РёР±РєР° РґРѕСЃС‚СѓРїР°: СЃС‚Р°С‚СѓСЃ {response.status}")
                    return None
                html = await response.text()

        # 1. РўР•РњРџР•Р РђРўРЈР Рђ
        temp = "РЅ/Рґ"
        t_match = re.search(r'"temperatureAir":\s?\[\s?(-?\d+)', html)
        if t_match:
            temp = t_match.group(1)

        # 2. РЈР¤-РРќР”Р•РљРЎ (8 Р·РЅР°С‡РµРЅРёР№)
        uv_all = []
        uv_sect = re.search(r'data-key=radiation.*?<div class="widget-row', html, re.S)
        if uv_sect:
            uv_all = [int(n) for n in re.findall(r'>\s*(\d+)\s*<', uv_sect.group(0))]

        # 3. KP-РРќР”Р•РљРЎ (8 Р·РЅР°С‡РµРЅРёР№)
        kp_all = []
        start_index = html.find('data-key=geomagnetic')
        if start_index != -1:
            kp_block = html[start_index : start_index + 5000]
            kp_all = [int(n) for n in re.findall(r'class="[^"]*item-(\d)"', kp_block)]
        
        # РћР±СЂРµР·Р°РµРј СЃРїРёСЃРєРё РґРѕ 8 Р·РЅР°С‡РµРЅРёР№ (СЃСѓС‚РєРё)
        kp_all = kp_all[:8]
        uv_all = uv_all[:8]
        
        # РћРїСЂРµРґРµР»СЏРµРј РёРЅРґРµРєСЃ С‚РµРєСѓС‰РµРіРѕ РІСЂРµРјРµРЅРё (РєР°Р¶РґС‹Рµ 3 С‡Р°СЃР°)
        idx = datetime.now().hour // 3
        
        # Р¤РѕСЂРјРёСЂСѓРµРј РёС‚РѕРіРѕРІС‹Р№ СЃР»РѕРІР°СЂСЊ РґР»СЏ Р±РѕС‚Р°
        res = {
            "temp": temp,
            "uv_current": uv_all[idx] if idx < len(uv_all) else (uv_all[-1] if uv_all else 0),
            "kp_current": kp_all[idx] if idx < len(kp_all) else (kp_all[-1] if kp_all else 0),
            "uv_list": uv_all, # Р”Р»СЏ СЃС‚СЂРµР»РѕС‡РµРє РІ РўР“
            "kp_list": kp_all, # Р”Р»СЏ СЃС‚СЂРµР»РѕС‡РµРє РІ РўР“
            "max_uv": max(uv_all) if uv_all else 0,
            "max_kp": max(kp_all) if kp_all else 0
        }

        # --- Р—РђРџРРЎР¬ Р’ MYSQL (0.194) ---
        # Р’С‹РїРѕР»РЅСЏРµРј РІ РѕС‚РґРµР»СЊРЅРѕРј РїРѕС‚РѕРєРµ, С‡С‚РѕР±С‹ РЅРµ С‚РѕСЂРјРѕР·РёС‚СЊ Р°СЃРёРЅС…СЂРѕРЅРЅРѕСЃС‚СЊ
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
                
                query = """
                    INSERT INTO weather_log 
                    (temp, uv_current, kp_current, kp_list, uv_list, max_uv, max_kp) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                
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
                conn.commit() # Р‘РђР—Рђ РџРћР”РўР’Р•Р Р”РР›Рђ Р—РђРџРРЎР¬
                
                print("вњ… Р”Р°РЅРЅС‹Рµ РІ Р‘Р” СЃРѕС…СЂР°РЅРµРЅС‹. РћС‚РїСЂР°РІР»СЏРµРј РІ MQTT...")

                # --- Р’РћРў Р—Р”Р•РЎР¬ РќРђР§РРќРђР•РўРЎРЇ РњРђР“РРЇ MQTT ---
                import os
                # РћС‚РїСЂР°РІР»СЏРµРј С‚РµРјРїРµСЂР°С‚СѓСЂСѓ РЅР° Р”Р°С‡Сѓ (РёСЃРїРѕР»СЊР·СѓРµРј РёРјСЏ РёР· AdGuard!)
                # Р—Р°РјРµРЅРёС‚Рµ IDX РЅР° РІР°С€Рё СЂРµР°Р»СЊРЅС‹Рµ РЅРѕРјРµСЂР° РґР°С‚С‡РёРєРѕРІ РІ Domoticz
                os.system(f"mosquitto_pub -h dacha -t 'domoticz/in' -m '{{\"command\": \"udevice\", \"idx\": 14, \"svalue\": \"{res['temp']}\"}}'")
                os.system(f"mosquitto_pub -h dacha -t 'domoticz/in' -m '{{\"command\": \"udevice\", \"idx\": 15, \"svalue\": \"{res['uv_current']}\"}}'")
                
                print("рџ“Ў Р”Р°РЅРЅС‹Рµ СѓСЃРїРµС€РЅРѕ СѓР»РµС‚РµР»Рё РЅР° Р”Р°С‡Сѓ!")
                
                cursor.close()
                conn.close()
            except Exception as db_e:
                print(f"вќЊ РћС€РёР±РєР°: {db_e}")

        return res

    except Exception as e:
        print(f"РћС€РёР±РєР° РІ analyze.py: {e}")
        return None

# РўРµСЃС‚
if __name__ == "__main__":
    result = asyncio.run(get_weather_analysis())
    print(result)


        
        
