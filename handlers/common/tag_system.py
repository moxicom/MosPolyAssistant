import logging

from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.dispatcher import FSMContext
from config import bot

from aiogram.dispatcher.filters.state import State, StatesGroup
from handlers import general
from Db import db_functions as db


logger = logging.getLogger('[LOG-TagSystem]')
internal_error_msg = "Внутрисерверная ошибка. Повторите попытку. При повторении ошибки обратитесь к администраторам"


class States(StatesGroup):
    PROCESS = State()          # state to use menu


async def button_imitation(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Нажми", reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("Вызвать меню", callback_data="cancel_tag_system")))


async def start(callback_query: types.CallbackQuery, state: FSMContext):
    """Updates data of state and invokes `invoke_tag_system` function"""
    await callback_query.answer()
    await state.finish()
    try:
        group_id = await general.get_group_id_by_tg_id(tg_id=callback_query.from_user.id)
        await state.update_data(group_id = group_id)
        logger.info("Updated data with `group_id`")
    except Exception as ex:
        logger.exception("Exception while updating group_id")
        logger.warning("Update group_id state error")
        await bot.send_message(callback_query.from_user.id, internal_error_msg)
        await state.finish()
        return
    await States.PROCESS.set()
    await invoke_tag_system(callback_query, state)


async def invoke_tag_system(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer()


async def cancel_tag_system(callback_query: types.CallbackQuery, state: FSMContext):
    logger.info("Cancel button pressed")
    try:
        await bot.answer_callback_query(callback_query.id)
        await bot.delete_message(callback_query.message.chat.id, callback_query.message.message_id)
        await bot.send_message(callback_query.message.chat.id, "Вы отменили текущее действие. В случае необходимости \nнажмите на > /help < Или напишите эту команду в чат")
    except Exception:
        await state.finish()


def tag_system_handlers(dp: Dispatcher):
    dp.register_message_handler(button_imitation, commands=['tag_menu'])
    dp.register_callback_query_handler(start, lambda c: c.data == "cancel_tag_system", state="*")

