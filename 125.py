
import platform
import subprocess

def ping_ip(ip):
    # Определение параметров команды в зависимости от ОС
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    command = ['ping', param, '1', '-w', '1000', ip] # -W 1 — таймаут 1 сек
    print(command)
    # Выполнение команды
    result = subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    return result.returncode == 0

# Использование
target_ip = "192.168.0.1"
if ping_ip(target_ip):
    print(f"IP {target_ip} доступен")
else:
    print(f"IP {target_ip} недоступен") 