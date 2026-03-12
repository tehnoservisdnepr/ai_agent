import paramiko
from aiogram import types
from aiogram.filters import Command

# Данные для подключения к серверу Domoticz
SSH_HOST = '192.168.1.X'  # IP вашего сервера
SSH_USER = 'your_user'    # Имя пользователя (например, pi)
# Путь к приватному ключу (рекомендуется) или пароль
SSH_KEY_PATH = '/home/user/.ssh/id_rsa' 

def execute_remote_reboot():
    """Функция для отправки команды перезагрузки через SSH."""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        # Подключение по ключу
        ssh.connect(SSH_HOST, username=SSH_USER, key_filename=SSH_KEY_PATH, timeout=10)
        
        # Команда на перезагрузку (sudo требует отсутствия запроса пароля в visudo)
        # Или можно перезапустить только сервис Domoticz:
        # stdin, stdout, stderr = ssh.exec_command('sudo systemctl restart domoticz.service')
        
        stdin, stdout, stderr = ssh.exec_command('sudo reboot')
        
        return True, "Команда на перезагрузку отправлена успешно."
    except Exception as e:
        return False, f"Ошибка подключения: {str(e)}"
    finally:
        ssh.close()

@dp.message(Command("reboot_domoticz"))
async def cmd_reboot(message: types.Message):
    # Проверка прав (например, только для вашего ID)
    if message.from_user.id != ВАШ_ТЕЛЕГРАМ_ID:
        return await message.answer("У вас нет прав на эту операцию.")

    await message.answer("Попытка перезагрузки сервера Domoticz...")
    success, result_text = execute_remote_reboot()
    await message.answer(result_text)