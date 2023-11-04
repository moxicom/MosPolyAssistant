from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

#token = '5983840222:AAH5nLq35iCpMvSRBsD6v8p5TqhL_kmLSXU'
token = '<token>'

storage = MemoryStorage()
bot = Bot(token=token)
dp = Dispatcher(bot, storage=storage)
