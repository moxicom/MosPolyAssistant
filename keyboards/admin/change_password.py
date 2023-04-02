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
from start_bot import bot
from keyboards import main_keyboards as keyboards
from Db import db_functions as db
from handlers import general


class MyStates(StatesGroup):
    FIRST_WORD = State()
    SECOND_WORD = State()


# Проверка на то что сообщение является командой, сюда добавятся команды основные, если есть
# @dp.message_handler(Command(["start"]))
async def start_handler(message: types.Message, state: FSMContext):
    if message.text == '/start':
        await state.finish()
        await start(message)


# Старт бота
async def start(message: types.Message):
    markup = InlineKeyboardMarkup().add(InlineKeyboardButton("Изменить пароль", callback_data="change_password"))
    await bot.send_message(chat_id=message.chat.id, text="Привет, что ты хочешь сделать?", reply_markup=markup)
    await MyStates.FIRST_WORD.set()


def cancel_button_markup():
    return InlineKeyboardMarkup().add(InlineKeyboardButton("Отменить", callback_data="cancel"))


# @dp.callback_query_handler(lambda c: c.data == "change_password", state="*")
async def change_password(callback_query: types.CallbackQuery, state: FSMContext):
    try:
        await bot.answer_callback_query(callback_query.id)
        await bot.send_message(callback_query.from_user.id, "Введите пароль:", reply_markup=cancel_button_markup())
        await MyStates.FIRST_WORD.set()
    except Exception as ex:
        await bot.answer_callback_query(callback_query.id, text="Ошибка" + str(ex))
        await state.finish()


# @dp.callback_query_handler(lambda c: c.data == "cancel", state="*")
async def cancel(callback_query: types.CallbackQuery, state: FSMContext):
    try:
        await bot.answer_callback_query(callback_query.id)
        await start(callback_query.message)
        await state.finish()
    except Exception as ex:
        await bot.answer_callback_query(callback_query.id, text="Ошибка" + str(ex))
        await state.finish()


# Для первого ввода пароля
# @dp.message_handler(Text, state=MyStates.FIRST_WORD)
async def process_first_word(message: types.Message, state: FSMContext):
    # async with state.proxy() as data:
    try:
        if message.text.startswith("/"):
            await start_handler(message, state)
        else:
            async with state.proxy() as data:
                data['first_word'] = message.text
            await message.reply("Введите пароль повторно:", reply_markup=cancel_button_markup())
            await MyStates.SECOND_WORD.set()
    except Exception as ex:
        await message.reply('Ошибка ' + str(ex))
        await state.finish()


# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# Для второго, тут проверка и добавление в бд
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# @dp.message_handler(Text, state=MyStates.SECOND_WORD)
async def process_second_word(message: types.Message, state: FSMContext):
    try:
        if message.text.startswith("/"):
            await start_handler(message, state)
        else:
            async with state.proxy() as data:
                first_word = data['first_word']
                second_word = message.text
                if first_word == second_word:
                    data['password'] = str(hashlib.sha256(second_word.encode()).hexdigest())
                    # ВОТ ТУТ БУДЕТ ЗАМЕНА В БД Я НЕ ПОНЯЛА КАК
                    # await db.insert_groups_info(group_name=data['group'], password=data['password'])
                    await message.reply("Пароль успешно изменен")
                    await state.finish()
                    await start(message)
                else:
                    await message.reply("Пароли не совпадают, попробуйте еще раз:",
                                        reply_markup=cancel_button_markup())
                    await MyStates.SECOND_WORD.set()
    except Exception as ex:
        await message.reply('Ошибка ' + str(ex))
        await state.finish()
