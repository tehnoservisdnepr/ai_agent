#Python
import asyncio
import os
import platform
import subprocess
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message

# --- НАСТРОЙКИ ---
API_TOKEN = '8662331180:AAGMjopUD1sE5rKhQNmoMjaEHcN62UQjTUY'
# Список важных IP для мониторинга (например, инвертор, BMS, сервер)



WATCHLIST = {
    "192.168.0.1"  : "Роутер      ",
    "192.168.0.166": "Raspberry Pi",
    "192.168.0.176": "Desktop     ",
    "192.168.0.101": "Espressif)  ",
    "192.168.0.151": "Espressif   ",
    "192.168.0.186": "Espressif   ",
    "192.168.0.105": "zero 1      ",
    "192.168.0.109": "Espressif   "
}

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

def ping_ip(ip):
    """Проверяет доступность IP-адреса."""
    
     # Определяем ОС
    current_os = platform.system().lower()
    
    # Формируем флаги
    # Windows: -n (количество), -w (таймаут в мс)
    # Unix: -c (количество), -W (таймаут в сек)
    if current_os == "windows":
        command = ['ping', '-n', '1', '-w', '1000', ip]
        #print(command)
    else:
        command = ['ping', '-c', '1', '-W', '1', ip]
    
    try:
        # shell=False — это стандарт (безопаснее)
        result = subprocess.run(
            command, 
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.DEVNULL
        )
        return result.returncode == 0
    except Exception:
        return False
    
    
    # Параметры ping зависят от ОС (Windows -n, Linux -c)
    '''
    
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    command = ['ping', param, '1', '-w', '1000', ip]
    
    
    return subprocess.call(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0
    '''

@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "Привет! Я сетевой админ-бот.\n"
        "Доступные команды:\n"
        "/status - Проверить устройства из списка\n"
        "/scan - Быстрый скан подсети (первые 20 адресов)"
    )

@dp.message(Command("status"))
async def cmd_status(message: Message):
    status_report = "<b>Статус устройств:</b>\n"
    for ip, name in WATCHLIST.items():
    #for ip in WATCHLIST():    
        is_online = "✅ Online" if ping_ip(ip) else "❌ Offline"
        status_report += f"• {name} ({ip}): {is_online}\n"
      
    await message.answer(status_report, parse_mode="HTML")

@dp.message(Command("scan"))
async def cmd_scan(message: Message):
    wait_msg = await message.answer("Сканирую сеть, подождите...")
    base_ip = "192.168.0." # Укажите свою подсеть
    online_devices = []

    # Сканируем ограниченный диапазон, чтобы не заставлять бота ждать слишком долго
    for i in range(1, 21): 
        ip = f"{base_ip}{i}"
        #print(ip)
        if ping_ip(ip):
            online_devices.append(ip)
    
    if online_devices:
        response = "<b>Найдены устройства:</b>\n" + "\n".join(online_devices)
    else:
        response = "Устройств не обнаружено."
        
    await wait_msg.edit_text(response, parse_mode="HTML")

async def main():
    print("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен.")