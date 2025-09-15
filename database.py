import aiosqlite
from config import DB_PATH

# Создание таблицы, если не существует
async def create_table():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS user_results (
                user_id INTEGER PRIMARY KEY,
                score INTEGER
            )
        ''')
        await db.commit()

# Сохранить результат квиза
async def save_result(user_id: int, score: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            INSERT INTO user_results (user_id, score)
            VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET score=excluded.score
        ''', (user_id, score))
        await db.commit()

# Получить последний результат пользователя
async def get_result(user_id: int) -> int | None:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute('SELECT score FROM user_results WHERE user_id = ?', (user_id,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else None