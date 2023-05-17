from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

#token = '5983840222:AAH5nLq35iCpMvSRBsD6v8p5TqhL_kmLSXU'
token = '5555273889:AAFh3yk1-P5brLJQ79Ip5_JbDydkJhAGUpc'

storage = MemoryStorage()
bot = Bot(token=token)
dp = Dispatcher(bot, storage=storage)