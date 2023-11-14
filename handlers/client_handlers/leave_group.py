import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import ContentTypeFilter

from aiogram.dispatcher.handler import CancelHandler
from typing import List, Union
from aiogram.dispatcher.middlewares import BaseMiddleware

from config import bot
from Db import db_functions as db


logging.basicConfig(level=logging.INFO)

YES_DATA = "leave_group_yes"
NO_DATA = "leave_group_no"


class Leave_group_state(StatesGroup):
    '''States for attachments'''
    CONFIRMATION = State()


async def leave_group_start(callback_query: types.CallbackQuery, state: FSMContext):
    try:
        await callback_query.answer()
        await state.finish()
    except Exception:
        pass
    mkp = InlineKeyboardMarkup()
    mkp.add(InlineKeyboardButton("Да", callback_data=YES_DATA), InlineKeyboardButton("Нет", callback_data=NO_DATA))
    await bot.edit_message_text(text="Вы точно хотите выйти из группы", chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id,  reply_markup=mkp)
    await Leave_group_state.CONFIRMATION.set()


async def leave_group_accept(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer()
    try:
        tg_id = callback_query.from_user.id
        id = await db.fetch_users(tg_id)
        await db.delete_group_member(id[0][0])
        await db.delete_user(tg_id)
        await bot.delete_message(callback_query.message.chat.id, callback_query.message.message_id)
    except Exception as ex:
        logging.warning(f"leave_group_accept: {ex}")
        await bot.send_message(callback_query.from_user.id, "Произошла ошибка, попробуйте позже")
    await state.finish()
    await bot.send_message(callback_query.message.chat.id, "Вы успешно вышли из группы")


async def leave_group_refuse(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer()
    await bot.edit_message_text(text="Для вызова основного меню напишите: /help", chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id,reply_markup=None)
    await state.finish()


def leave_group_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(leave_group_start, lambda c: c.data == "leave_group_start")
    dp.register_callback_query_handler(leave_group_accept, lambda c: c.data == YES_DATA, state=Leave_group_state.CONFIRMATION)
    dp.register_callback_query_handler(leave_group_refuse, lambda c: c.data == NO_DATA, state=Leave_group_state.CONFIRMATION)
