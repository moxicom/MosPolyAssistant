from aiogram import types, Dispatcher
from config import bot

from handlers import general
from keyboards import main_keyboards as keyboards


async def check_profile(message: types.Message):
    pass


async def start_interaction(message: types.Message):
    exist = await general.check_user_existence(message.from_user.id)
    if (exist):
        role = await general.get_role_by_tg_id(message.from_user.id)
        if role == 2:
            await message.reply("Добро пожаловать, староста", reply_markup=keyboards.admin_functions_mkp)
        elif role == 0:
            await message.reply("Добро пожаловать")
        else:
            bot.send_message(message.from_user.id, "что-то пошло не так")
    else:
        await bot.send_message(message.from_user.id, "Вы отсутствуете в базе данных.\n" +
                               "Чтоб зарегистрироваться напишите следующую команду:\n\t/reg")


async def help_command(message: types.Message):
    role = await general.get_role_by_tg_id(message.from_user.id)
    if role == 2:
        await message.reply("Вот что ты можешь сделать", reply_markup=keyboards.admin_functions_mkp)
    elif role == 0:
        await message.reply("Вот что ты можешь сделать")
    else:
        bot.send_message(message.from_user.id, "что-то пошло не так")


def start_interactions_handlers(dp: Dispatcher):
    dp.register_message_handler(start_interaction, commands=['start'])
    dp.register_message_handler(help_command, commands=['help'])
