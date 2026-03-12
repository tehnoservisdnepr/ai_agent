from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
import asyncio
#from aiogram.utils.markdown import code
#from aiogram.utils.markdown import hcode, quote_html # Для HTML
from aiogram.utils.markdown import code
# Вставьте ваш токен
TOKEN = '8662331180:AAGMjopUD1sE5rKhQNmoMjaEHcN62UQjTUY'

dp = Dispatcher()

@dp.message(CommandStart())
async def command_start_handler(message: types.Message):
    # message.from_user.id — это и есть ваш уникальный Telegram ID
    user_id = message.from_user.id
    
    print(f"User ID: {user_id}") # Выведет в консоль сервера
    
    await message.answer(rf"Привет\! Твой Telegram ID: `{user_id}`", parse_mode="MarkdownV2")
    #await message.answer(f"Привет! Твой Telegram ID: <code>{user_id}</code>", parse_mode="HTML")
async def main():
    bot = Bot(token=TOKEN)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    
    # 887949813
    