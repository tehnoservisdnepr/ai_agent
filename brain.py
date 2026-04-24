import json
import os
import subprocess

def load_config():
    # Путь к конфигу остается прежним
    with open('core/network_map.json', 'r') as f:
        return json.load(f)

def ping(host):
    # Пинг по 2 пакета, таймаут 1 секунда
    command = ['ping', '-c', '2', '-W', '1', host]
    return subprocess.call(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0

def check_network():
    config = load_config()
    nodes = config.get('nodes', {})

    print(f"--- Отчет Боцмана v1.2: Проверка присутствия ---")

    for name, data in nodes.items():
        print(f"\nПроверяю узел: {name} ({data.get('comment', '')})")
        interfaces = data.get('interfaces', {})
        node_type = data.get('type', 'static') # По умолчанию считаем узел статичным

        status_ok = False
        
        # ЛОГИКА ДЛЯ МОБИЛЬНИКА (ROAMING)
        if node_type == 'roaming':
            for iface_type, address in interfaces.items():
                if ping(address):
                    print(f"  [OK] Мастер обнаружен через {iface_type}: {address}")
                    status_ok = True
                    break # Нашли в одной сети — этого достаточно, выходим из цикла интерфейсов
            
            if not status_ok:
                print(f"  [-] Мастер не найден ни в одной из сетей (Home/Orlika/Dacha/Netbird)")

        # ЛОГИКА ДЛЯ СЕРВЕРОВ (STATIC)
        else:
            for iface_type, address in interfaces.items():
                if ping(address):
                    print(f"  [OK] {iface_type}: {address}")
                    status_ok = True
                else:
                    print(f"  [FAIL] {iface_type}: {address}")

        # ФИНАЛЬНЫЙ ВЕРДИКТ
        if not status_ok:
            if data.get('critical'):
                print(f"  !! ВНИМАНИЕ !! Критический узел {name} недоступен. Якорь всплыл!")
            else:
                print(f"  [!] Узел {name} сейчас вне зоны доступа.")

if __name__ == "__main__":
    if not os.path.exists('core/network_map.json'):
        print("Ошибка: Файл конфигурации не найден! Создай папку core и положи туда network_map.json")
    else:
        check_network()

