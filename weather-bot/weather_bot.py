import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# Твои рабочие модули
from analyze import get_weather_analysis
from ai_engine import get_ai_verdict
from api_token import TELEGRAM_TOKEN

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

# --- ЛОКАЛЬНАЯ ЛОГИКА (Работает без квот и интернета) ---
def get_local_opinion(kp, uv, temp):
    opinion = "✅ Все системы в норме. "
    try:
        kp_val = float(kp) if kp != 'н/д' else 0
        uv_val = float(uv) if uv != 'н/д' else 0
        temp_val = float(temp)
        
        if kp_val >= 5:
            opinion += "🧲 Магнитная буря! Возможны помехи в связи и работе инверторов. "
        if uv_val >= 6:
            opinion += "☀️ Высокий УФ! Берегите глаза и кожу. "
        if temp_val > 45: # Порог для электроники
            opinion += "🔥 Внимание! Orange Pi нагрелся выше нормы, проверьте охлаждение."
    except Exception:
        opinion = "📊 Данные получены, приступаю к мониторингу."
    return opinion

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Привет! Гляжу в Meteofor, слежу за инверторами и погодой. Жми /status")

@dp.message(Command("status"))
async def cmd_status(message: types.Message):
    # 1. Тянем погоду через analyze.py
    res = await get_weather_analysis()
    
    if res:
        uv_list = res.get('uv_list', [])
        kp_list = res.get('kp_list', [])
        
        # Тренды (разделитель — три пробела)
        uv_trend = "   ".join(map(str, uv_list)) if uv_list else str(res.get('uv_current', 'н/д'))
        kp_trend = "   ".join(map(str, kp_list)) if kp_list else str(res.get('kp_current', 'н/д'))

        # 2. Попытка получить вердикт от ИИ (если квоты позволяют)
        ai_context = (
            f"Погода в Днепре: {res['temp']}°C. "
            f"Kp: {res.get('kp_current', 'н/д')}. "
            f"УФ: {res.get('uv_current', 'н/д')}. "
            f"Прогноз Кр: {kp_trend}. "
            f"Прогноз Уф: {uv_trend}. "
            f"Дай краткий совет по здоровью и электронике (инверторы, АКБ)."
        )
        
        try:
            raw_ai = await get_ai_verdict(ai_context)
            if isinstance(raw_ai, dict):
                ai_opinion = raw_ai.get('reason', 'Нет данных')
            else:
                ai_opinion = raw_ai
                
            # Если API выдало ошибку квоты (429), переходим на локальный анализ
            if "RESOURCE_EXHAUSTED" in str(ai_opinion) or "429" in str(ai_opinion):
                ai_opinion = get_local_opinion(res.get('kp_current', 0), res.get('uv_current', 0), res['temp'])
                ai_label = "🤖 **АНАЛИЗ (Локальный):**"
            else:
                ai_label = "🤖 **АНАЛИЗ ИИ:**"
        except:
            ai_opinion = get_local_opinion(res.get('kp_current', 0), res.get('uv_current', 0), res['temp'])
            ai_label = "🤖 **АНАЛИЗ (Локальный):**"

        # 3. Сборка финального сообщения
        text = (
            f"📊 **ТЕКУЩИЙ СТАТУС:**\n\n"
            f"🌍 Днепр (Meteofor):\n"
            f"🌡 Температура: {res['temp']}°C\n"
            f"🟢 Текущий Kp: `{res.get('kp_current', 'н/д')}`\n"
            f"🛡 Текущий УФ: `{res.get('uv_current', 'н/д')}`\n"
            f"🧲 Kp-динамика: `{kp_trend}`\n"
            f"☀️ УФ-динамика: `{uv_trend}`\n\n"
            f"{ai_label}\n{ai_opinion}\n\n"
            f"🧐 _Помни: данные из аэропорта, верь своим чувствам!_"
        )
        
        await message.answer(text, parse_mode="Markdown")
    else:
        await message.answer("❌ Meteofor молчит...")
        
async def main():
    while True:
        try:
            logging.info("Запуск бота...")
            await dp.start_polling(bot)
        except Exception as e:
            logging.error(f"Критическая ошибка: {e}")
            logging.info("Перезапуск через 30 секунд...")
            await asyncio.sleep(30) 

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Бот остановлен")