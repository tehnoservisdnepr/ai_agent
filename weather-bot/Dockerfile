# Используем легкий образ Python 3.12
FROM python:3.12-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем системные зависимости и создаем пользователя для безопасности
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -m botuser

# Копируем только требования для кэширования слоев
COPY requirements.txt .

# Устанавливаем библиотеки
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код и меняем владельца файлов на botuser
COPY --chown=botuser:botuser . .

# Переключаемся на обычного пользователя
USER botuser

# Команда для запуска
CMD ["python", "-u", "weather_bot.py"]