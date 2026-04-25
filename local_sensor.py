import asyncio
import aiomqtt
import json
import psutil
import socket

# Константы
MQTT_BROKER = "192.168.0.166" # IP твоего главного узла с брокером
POLL_INTERVAL = 300           # 5 минут (золотой стандарт мониторинга)

async def get_metrics():
    """Собирает реальные показатели железа"""
    hostname = socket.gethostname()
    
    # Пытаемся найти температуру (зависит от драйверов ядра)
    temp = 0
    temps = psutil.sensors_temperatures()
    for name in ['cpu_thermal', 'cpu-thermal', 'soc_thermal']:
        if name in temps:
            temp = temps[name][0].current
            break

    return {
        "hostname": hostname,
        "ip": socket.gethostbyname(hostname + ".local") if ".local" in hostname else "127.0.0.1",
        "t": round(temp, 1),
        "l": psutil.cpu_percent(),
        "f": round(psutil.disk_usage('/').free / (1024**3), 1)
    }

async def main():
    print(f"🚀 Сенсор {socket.gethostname()} запущен. Протокол: Git/MQTT")
    
    while True:
        try:
            async with aiomqtt.Client(MQTT_BROKER) as client:
                data = await get_metrics()
                topic = f"nii/v1/{data['hostname']}/tele"
                
                await client.publish(topic, json.dumps(data))
                print(f"📡 [MQTT] Отправлено в {topic}: {data['t']}°C")
                
            await asyncio.sleep(POLL_INTERVAL)
            
        except Exception as e:
            print(f"⚠️ Ошибка связи: {e}. Повтор через 30 сек...")
            await asyncio.sleep(30)

if __name__ == "__main__":
    asyncio.run(main())