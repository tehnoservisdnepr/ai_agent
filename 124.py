import platform
import subprocess

def ping_ip(ip):
    # Определяем ОС
    current_os = platform.system().lower()
    
    # Формируем флаги
    # Windows: -n (количество), -w (таймаут в мс)
    # Unix: -c (количество), -W (таймаут в сек)
    if current_os == "windows":
        command = ['ping', '-n', '1', '-w', '1000', ip]
        print(command)
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

# Использование
target_ip = "192.168.0.1" # Проверим публичный DNS Google
if ping_ip(target_ip):
    print(f"✅ IP {target_ip} доступен")
else:
    print(f"❌ IP {target_ip} недоступен")
  



  
 