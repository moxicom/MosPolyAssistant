from datetime import datetime
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from config import bot


from handlers import general
import handlers.admin.tags as tags
import handlers.admin.attachments as attachments


async def ask_for_attachments_necessity(callback_query: types.CallbackQuery, state: FSMContext):
    '''Ask user if he wants to add attachments to the message'''
    markup = InlineKeyboardMarkup().add(InlineKeyboardButton("Да", callback_data="yes")).add(InlineKeyboardButton("Нет", callback_data="no"))
    # await callback_query.answer()
    # await bot.send_message(callback_query.from_user.id, "Хотите ли вы добавить медиа? (Изображения, файлы, видео)",  reply_markup=markup)
    await bot.edit_message_text(
        text="Хотите ли вы добавить медиа? (Изображения, файлы, видео)",
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        reply_markup=markup
    )
    await tags.States.ATTACHMENTS.set()


async def ask_for_attachments_message(callback_query: types.CallbackQuery, state: FSMContext):
    '''Ask user if he wants to send attachments by one message - invokes when user used button with callback data `yes`'''
    await callback_query.answer()
    await bot.send_message(callback_query.from_user.id, "Отправьте медиафайлы, которые хотите прикрепить.")


async def received_attachments_handler(message: types.Message, state: FSMContext):
    '''Receive attachments from user -> to learn more check function inside'''
    await attachments.receive_message_with_media(message, state, reply_keyboard_text="Продолжить")
     

async def end_process_click_handler (message: types.Message, state: FSMContext):
    '''End addition attachments process'''
    await tags.confirm_full_message(message, state)


async def decline_attachments(callback_query: types.CallbackQuery, state: FSMContext):
    '''Decline attachments - invokes when user used button with callback data `no`'''
    await tags.confirm_full_message(callback_query.message, state)

async def get_attachments(state: FSMContext):
    '''Returns MediaInput from state data.'''
    return await attachments.get_state_media_group(state)

async def send_attachments(media, chat_id, state):
    await attachments.send_state_media_group(media, chat_id, state)
