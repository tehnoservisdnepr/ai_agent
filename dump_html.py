#---------------------------------------------------------
# Скрипт-шпион для захвата сырого HTML с Meteofor
# Дата: 04.04.2026
# Цель: Понять, как "клоуны" прячут Kp-индекс
#---------------------------------------------------------

import requests

def save_meteofor_dump():
    url = "https://www.meteofor.com.ua/weather-dnipro-5077/"
    # Используем заголовки, чтобы сайт думал, что мы — обычный браузер
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        print(f"📡 Запрашиваю данные с {url}...")
        response = requests.get(url, headers=headers, timeout=15)
        
        # Проверяем успешность запроса
        if response.status_code == 200:
            html_content = response.text
            
            # Сохраняем весь HTML в файл для препарирования
            with open("meteofor_dump.txt", "w", encoding="utf-8") as f:
                f.write(html_content)
            
            print("✅ УСПЕХ! Полный код страницы сохранен в файл: meteofor_dump.txt")
            print("🔍 ИНСТРУКЦИЯ:")
            print("1. Открой файл 'meteofor_dump.txt' в текстовом редакторе (Notepad++, VS Code).")
            print("2. Нажми Ctrl + F и ищи слово 'geomagnetic'.")
            print("3. Посмотри, какие цифры стоят рядом в тегах или атрибутах.")
        else:
            print(f"❌ Ошибка сервера: Код {response.status_code}")

    except Exception as e:
        print(f"💥 Критическая ошибка при дампе: {e}")

if __name__ == "__main__":
    save_meteofor_dump()