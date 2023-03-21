from aiogram import types, Dispatcher
from start_bot import bot

from handlers import general


async def check_profile(message: types.Message):
    pass


async def start_interaction(message: types.Message):
    exist = await general.check_user_existence(message.from_user.id)
    if (exist):
        await message.reply("Вы существуете в базе данных")
    else:
        await bot.send_message(message.from_user.id, "Вы отсутствуете в базе данных.\n" +
                          "Чтоб зарегистрироваться напишите следующую команду:\n\t/reg")


def start_interaction_handlers(dp: Dispatcher):
    dp.register_message_handler(start_interaction, commands=['start'])