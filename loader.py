import logging

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram import types
from data.config import TG_TOKEN

bot = Bot(token=TG_TOKEN, parse_mode=types.ParseMode.HTML)

#Хранилище для машины состояний
storage = MemoryStorage()

#запуск диспетчера бота
dp = Dispatcher(bot, storage=storage)
logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s',
                    level=logging.INFO,
                    )
