import asyncio
import aiomysql
import re

# Данные для подключения (замени на свои)
DB_CONFIG = {
    'host': 'localhost',
    'user': 'tom',
    'password': 'vash_parol', # Тот, что ты задал для пользователя tom
    'db': 'nii_hub'
}

LOG_FILE = 'hunter.log'

async def migrate():
    # Регулярка для выцепления новости и оценки
    # Ищем "Новость: <название>" и ближайшее "Оценка ИИ: <балл>/10"
    pattern = re.compile(r"Новость: (.*?)\n.*?Оценка ИИ: (\d+)/10", re.DOTALL)
    
    with open(LOG_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    matches = pattern.findall(content)
    print(f"Найдено записей для переноса: {len(matches)}")

    pool = await aiomysql.create_pool(**DB_CONFIG)
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            for title, score in matches:
                # Вставляем данные. Если новость с таким заголовком уже есть, 
                # можем просто игнорировать или обновлять (тут просто вставляем)
                await cur.execute(
                    "INSERT INTO hunter_analytics (title, score) VALUES (%s, %s)",
                    (title.strip(), int(score))
                )
            await conn.commit()
    
    pool.close()
    await pool.wait_closed()
    print("Миграция завершена успешно!")

if __name__ == '__main__':
    asyncio.run(migrate())