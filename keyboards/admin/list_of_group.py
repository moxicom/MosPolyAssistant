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


async def send_list_of_group(callback_query: types.CallbackQuery, state: FSMContext):  # FSM password
    async with state.proxy() as data:
        try:
            group_info_fetch = await db.fetch_groups_info(group_name=data['group'])
            answer = callback_query.data
            message_id = callback_query.message.message_id
            chat_id = callback_query.message.chat.id

            # If the "Return" button is pressed, go back to the previous state
            if answer == "return":
                await bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id, reply_markup=None)
                await state.finish()
                # await send_message_with_buttons(chat_id)
                await MyStates.CHOOSING.set()
            else:
                await bot.answer_callback_query(callback_query.id)
                if answer == "Список участников":
                    text = db.fetch_groups_members(group_id=group_info_fetch[0][0])
                button_return = InlineKeyboardButton("Return", callback_data="return")
                markup = InlineKeyboardMarkup().add(button_return)
                await bot.edit_message_text(text, chat_id, message_id, reply_markup=markup)
        except Exception as ex:
            logging.exception(ex)
            await bot.answer_callback_query(callback_query.id, text="Ошибка" + str(ex))


def list_of_group_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(send_list_of_group, lambda c: c.data == "list_of_group", state="*")

