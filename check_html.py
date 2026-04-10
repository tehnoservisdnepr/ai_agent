import asyncio
import aiohttp

async def check():
    url = "https://www.meteofor.com.ua/ru/weather-dnipro-5077/"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url) as resp:
            html = await resp.text()
            # Ищем кусок кода, где обычно живет текущая погода
            # Берем первые 500 символов после слова "now" или "current"
            start = html.find('current')
            if start != -1:
                print("--- ОТРЫВОК HTML ---")
                print(html[start:start+1000]) 
            else:
                print("Слово 'current' не найдено, выводим начало страницы:")
                print(html[:1000])

asyncio.run(check())