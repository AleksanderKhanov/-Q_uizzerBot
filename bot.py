import asyncio
import logging
import nest_asyncio
from aiogram import Bot, Dispatcher

from config import API_TOKEN
from database import create_table
from handlers import register_handlers

nest_asyncio.apply()
logging.basicConfig(level=logging.INFO)

# Создаём экземпляры бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Регистрируем хэндлеры
register_handlers(dp, bot)

# Главная функция запуска бота
async def main():
    await create_table()  # создаём таблицу, если не существует
    await dp.start_polling(bot)


# Запуск
if __name__ == "__main__":
    asyncio.run(main())
