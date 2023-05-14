from aiogram import types, Dispatcher
from config import bot

from handlers import general
from keyboards import main_keyboards as k

async def check_profile(message: types.Message):
    pass


async def start_interaction(message: types.Message):
    exist = await general.check_user_existence(message.from_user.id)
    if (exist):
        await message.reply("Вы существуете в базе данных", reply_markup=k.admin_functions_mkp)
    else:
        await bot.send_message(message.from_user.id, "Вы отсутствуете в базе данных.\n" +
                          "Чтоб зарегистрироваться напишите следующую команду:\n\t/reg")


def start_interactions_handlers(dp: Dispatcher):
    dp.register_message_handler(start_interaction, commands=['start'])