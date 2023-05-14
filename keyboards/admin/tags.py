import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import ParseMode
from aiogram.utils.markdown import text, quote_html
from config import bot
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher.filters import Command

from aiogram.dispatcher.filters.state import State, StatesGroup

# API_TOKEN = ''
# #
# # logging.basicConfig(level=logging.INFO)
# bot = Bot(token=API_TOKEN)
# dp = Dispatcher(bot, storage=MemoryStorage())

existing_tags = []


class States(StatesGroup):
    MESSAGE = State()
    CHOOSE_ACTION = State()
    EXISTING_TAG = State()
    NEW_TAG = State()


# @dp.message_handler(commands=['start'])
async def start(message: types.Message, state: FSMContext):
    markup = ReplyKeyboardRemove()
    await state.finish()
    await bot.send_message(chat_id=message.chat.id, text="Введите ваше сообщение:", reply_markup=markup)
    await States.MESSAGE.set()


# @dp.message_handler(state=States.MESSAGE)
async def ask_for_tag(message: types.Message, state: FSMContext):
    print('Обработка сообщения')
    user_text = message.text
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(InlineKeyboardButton("Существующий тег", callback_data="existing_tag"))
    markup.add(InlineKeyboardButton("Добавить новый тег", callback_data="new_tag"))

    await message.reply("Добавить тег?", reply_markup=markup)
    await state.update_data(user_text=user_text)
    await States.CHOOSE_ACTION.set()


# @dp.callback_query_handler(lambda c: c.data == "existing_tag", state=States.CHOOSE_ACTION)
async def process_callback_existing_tag(callback_query: types.CallbackQuery, state: FSMContext):
    print('кнопка существующий тег')
    if existing_tags:
        markup = InlineKeyboardMarkup(row_width=2)
        for tag in existing_tags:
            markup.add(InlineKeyboardButton(tag, callback_data=f"tag_{tag}"))
        await bot.edit_message_text(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id,
                                    text="Выберите тег:", reply_markup=markup)
        await States.EXISTING_TAG.set()
    else:
        await bot.answer_callback_query(callback_query.id, "Нет существующих тегов, пожалуйста, добавьте новый тег.",
                                        show_alert=True)


# @dp.callback_query_handler(lambda c: c.data == "new_tag", state=States.CHOOSE_ACTION)
async def process_callback_new_tag(callback_query: types.CallbackQuery, state: FSMContext):
    print('кнопка новый тег')
    await bot.send_message(chat_id=callback_query.from_user.id, text="Введите новый тег:")
    await States.NEW_TAG.set()


# @dp.message_handler(state=States.NEW_TAG)
async def add_new_tag(message: types.Message, state: FSMContext):
    print('добавляем новый тег')
    new_tag = message.text
    existing_tags.append(new_tag)
    user_text = (await state.get_data()).get('user_text')
    await message.reply(f"{user_text} {new_tag}")
    await state.finish()


# @dp.callback_query_handler(state=States.EXISTING_TAG)
async def process_callback_actual_existing_tag(callback_query: types.CallbackQuery, state: FSMContext):
    tag = callback_query.data[4:]
    async with state.proxy() as data:
        user_text = data['user_text']
    tagged_message = f"{user_text} {tag}"
    await bot.send_message(chat_id=callback_query.message.chat.id, text=tagged_message)
    # await callback_query.answer()
    await state.finish()


def tags_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(start, lambda c: c.data == "write_message", state="*")
    dp.register_message_handler(ask_for_tag, state=States.MESSAGE)
    dp.register_callback_query_handler(process_callback_existing_tag, lambda c: c.data == "existing_tag",
                              state=States.CHOOSE_ACTION)
    dp.register_callback_query_handler(process_callback_new_tag, lambda c: c.data == "new_tag", state=States.CHOOSE_ACTION)
    dp.register_message_handler(add_new_tag, state=States.NEW_TAG)
    dp.register_callback_query_handler(process_callback_actual_existing_tag, state=States.EXISTING_TAG)
