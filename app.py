from loader import bot, storage
from aiogram import executor
from handlers import dp

async def on_shutdown(dp):
    await bot.close()
    await storage.close()


if __name__ == '__main__':
    executor.start_polling(dp, on_shutdown=on_shutdown)
