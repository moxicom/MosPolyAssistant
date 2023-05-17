import asyncio
import hashlib
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters import Text, Command
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from config import bot
from keyboards import main_keyboards as keyboards
from Db import db_functions as db
from handlers import general


class MyStates(StatesGroup):
    CHOOSING = State()


# async def send_message_with_buttons(chat_id):
#     text = "Выберете опцию"
#     button1 = InlineKeyboardButton("Список участников", callback_data="list_of_group")
#     markup = InlineKeyboardMarkup().add(button1)
#     return await bot.send_message(chat_id, text, reply_markup=markup)


async def send_list_of_group(callback_query: types.CallbackQuery, state: FSMContext):
    try:
        await callback_query.answer()
        group_id = await general.get_group_id_by_tg_id(tg_id=callback_query.from_user.id)
        users = await db.fetch_users_in_group(group_id=group_id)
        user_names = sorted([user[1] for user in users])
        group_info = await db.fetch_group_info_by_id(group_id=group_id)
        group_name = group_info[1]
        user_names_string = '\n'.join(f"{i + 1}. {name}" for i, name in enumerate(user_names))
        chat_id = callback_query.message.chat.id
        await bot.send_message(chat_id=chat_id, text="Название группы:\n"+group_name+"\nСписок группы:\n" + user_names_string)
    except Exception as ex:
        logging.exception(ex)
        await bot.answer_callback_query(callback_query.id, text="Ошибка" + str(ex))


def list_of_group_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(send_list_of_group, lambda c: c.data == "list_of_group", state="*")
