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
    FIRST_WORD = State()
    SECOND_WORD = State()


def cancel_button_markup():
    return InlineKeyboardMarkup().add(InlineKeyboardButton("Отменить", callback_data="cancel"))


# @dp.callback_query_handler(lambda c: c.data == "change_password", state="*")
async def change_password(callback_query: types.CallbackQuery, state: FSMContext):
    try:
        await bot.answer_callback_query(callback_query.id)
        await bot.send_message(callback_query.from_user.id, "Введите пароль:", reply_markup=cancel_button_markup())
        await MyStates.FIRST_WORD.set()
    except Exception as ex:
        await bot.answer_callback_query(callback_query.from_user.id, text="Ошибка" + str(ex))
        await state.finish()





# Для первого ввода пароля
# @dp.message_handler(Text, state=MyStates.FIRST_WORD)
async def process_first_word(message: types.Message, state: FSMContext):
    # async with state.proxy() as data:
    try:
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
        async with state.proxy() as data:
            first_word = data['first_word']
            second_word = message.text
            if first_word == second_word:
                password = str(hashlib.sha256(second_word.encode()).hexdigest())
                group_id = await general.get_group_id_by_tg_id(tg_id=message.from_user.id)
                await db.change_group_info(id=group_id, field='password', new_value=password)
                await message.reply("Пароль успешно изменен")
                await state.finish()
            else:
                await message.reply("Пароли не совпадают, попробуйте еще раз:",
                                    reply_markup=cancel_button_markup())
                await MyStates.SECOND_WORD.set()
    except Exception as ex:
        await message.reply('Ошибка ' + str(ex))
        await state.finish()


async def cancel(callback_query: types.CallbackQuery, state: FSMContext):
    try:
        await state.finish()
        await callback_query.answer()
        role = await general.get_role_by_tg_id(callback_query.from_user.id)
        if role == 2:
            await bot.send_message(callback_query.from_user.id, "Вот что ты можешь сделать", reply_markup=keyboards.admin_functions_mkp)
        elif role == 0:
            await bot.send_message(callback_query.from_user.id, "Вот что ты можешь сделать")
        else:
            bot.send_message(callback_query.from_user.id, "что-то пошло не так")
    except Exception as ex:
        await bot.answer_callback_query(callback_query.id, text="Ошибка" + str(ex))
        await state.finish()
# @dp.callback_query_handler(lambda c: c.data == "cancel", state="*")
# async def cancel(callback_query: types.CallbackQuery, state: FSMContext):
#     try:
#         await bot.answer_callback_query(callback_query.id)
#         # await start(callback_query.message)
#         await state.finish()
#     except Exception as ex:
#         await bot.answer_callback_query(callback_query.id, text="Ошибка" + str(ex))
#         await state.finish()

def change_password_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(change_password, lambda c: c.data == "change_password", state="*")
    dp.register_callback_query_handler(cancel, lambda c: c.data == "cancel", state="*")
    dp.register_message_handler(process_first_word, Text, state=MyStates.FIRST_WORD)
    dp.register_message_handler(process_second_word, Text, state=MyStates.SECOND_WORD)
