from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

#token = '5983840222:AAH5nLq35iCpMvSRBsD6v8p5TqhL_kmLSXU'
token = '6855569017:AAGdX6uuZ0JOIeLeL0-YxMnqmmiwstkmBzo'

storage = MemoryStorage()
bot = Bot(token=token)
dp = Dispatcher(bot, storage=storage)
