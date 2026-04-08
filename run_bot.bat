@echo off
:loop
echo [%date% %time%] Zapusk bota...
:: Указываем путь к питону внутри твоего виртуального окружения
.venv\Scripts\python.exe weather_bot.py
echo [%date% %time%] Bot upal. Perezapusk cherez 5 sekund...
timeout /t 5
goto loop