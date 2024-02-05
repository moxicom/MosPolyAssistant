import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import ParseMode, InputMediaPhoto, ReplyKeyboardMarkup, KeyboardButton, InputMediaDocument, InputMediaVideo, ReplyKeyboardRemove, InputMediaAnimation
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import ContentTypeFilter

#
from aiogram.dispatcher.handler import CancelHandler
from typing import List, Union
from aiogram.dispatcher.middlewares import BaseMiddleware
#

from Db import db_attachmments as db_attachmments

from config import bot


logging.basicConfig(level=logging.INFO)

class Attachments_temp_state(StatesGroup):
    '''States for attachments'''
    ADDITION = State()
    CONFIRMATION = State()
    SENDING = State()


async def temp_start(message: types.Message, state: FSMContext):
    await message.answer('Добро пожаловать в админку по работе с аттачментами!\nОтправьте сообщение с любыми медиафайлами, которые хотите отправить пользователю.')
    await Attachments_temp_state.ADDITION.set()
    media_input = MediaInput()
    await state.update_data(media_input=media_input)

 
async def insert_attachment_command_handler(state: FSMContext, video=None, file=None, image=None, audio=None) -> bool:
    '''Command handler for inserting attachments to DB wit insert exceptions handling'''
    try:
        if video:
            await db_attachmments.insert_attachment(video=video.file_id)
        elif file:
            await db_attachmments.insert_attachment(file=file.file_id)
        elif image:
            await db_attachmments.insert_attachment(image=image.file_id)
        elif audio:
            await db_attachmments.insert_attachment(audio=audio.file_id)
    except Exception as e:
        logging.warning(f'|attachments/insert_attachment_command_handler| An error has occurred: {e}')
        await state.finish()
        return False
    return True


class MediaInput:
    def __init__(self):
        self.photos = []
        self.documents = []
        self.videos = []


async def update_state_with_media_group(message: types.Message, state: FSMContext):
    '''Update state with media group'''
    media_input = await state.get_data()
    media_input = media_input.get('media_input')
    if not media_input:
        logging.info(f'|attachments/update_state_with_media_group| MediaInput is None, creating new one')
        media_input = MediaInput()
    try:
        if message.photo:
            photo_id = message.photo[-1].file_id
            media_input.photos.append(photo_id)
            logging.info("Message added")

        elif message.video:
            media_input.videos.append(message.video.file_id)
            logging.info("Video added")
        
        elif message.document:
            media_input.documents.append(message.document.file_id)
            logging.info("Document added")
        
        await state.update_data(media_input=media_input)
        print()
        for i in message:
            print(i)
        print()
    except Exception as e:
        logging.warning(f'|attachments/update_state_with_media_group| An error has occurred: {e}')
        await state.finish()


async def get_state_media_group(state: FSMContext) -> MediaInput:
    '''Get media group from state'''
    media = MediaInput()
    try:
        async with state.proxy() as data:
            media_group : MediaInput = data['media_input']
            # photos = media_group.photos
            # documents = media_group.documents
            # videos = media_group.videos
            # for i in photos:
            #     print("Photo:", i)
            # for i in documents:
            #     print("Doc:", i)
            # for i in videos:
            #     print("Video:", i)
        media = media_group
    except Exception as e:
        logging.warning(f'|attachments/get_media_group| An error has occurred: {e}')
        await state.finish()
    return media


async def receive_message_with_media(message: types.Message, state: FSMContext, reply_keyboard_text: str = "Получить медиа"):
    '''Receives attachments from user, updates state with them, creates reply keyboard to continue message sending, ask user when each attachment were loaded'''
    await update_state_with_media_group(message=message, state=state)
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton(reply_keyboard_text))
    await bot.send_message(message.from_user.id, "Медиа загружено", reply_markup = keyboard)
    

async def send_state_media_group(media: MediaInput, chat_id, state: FSMContext):
    '''Handler for sending message with media'''
    try:
        logging.info(media)
        if media.photos:
            photos = list(map(lambda photo_id: InputMediaPhoto(photo_id), media.photos))
            await bot.send_media_group(chat_id, photos)

        if media.documents:
            documents = list(map(lambda document_id: InputMediaDocument(document_id), media.documents))
            await bot.send_media_group(chat_id, documents)

        if media.videos:
            # videos = list(map(lambda video_id: InputMediaVideo(video_id), media.videos))
            videos = [
                types.InputMediaVideo(
                    media=video_id,
                    supports_streaming=True,
                ) for video_id in media.videos
            ]
            await bot.send_media_group(chat_id, videos)
        
        await bot.send_message(chat_id, "Бот загрузил эти медиа", reply_markup=ReplyKeyboardRemove())
        await state.update_data(media_input=MediaInput())
    except Exception as ex:
        await bot.send_message(chat_id, f"Ошибка: {ex}", reply_markup=ReplyKeyboardMarkup())
        await state.finish()
    # await state.finish() ### !!!!!!!
    return

# def temp_attachments_handler(dp: Dispatcher):
#     dp.register_message_handler(temp_start, commands=['attachments'], state='*')
#     dp.register_message_handler(receive_message_with_media, state=Attachments_temp_state.ADDITION, content_types=[
#     types.ContentType.PHOTO,
#     types.ContentType.VIDEO,
#     types.ContentType.DOCUMENT,
#     ])
#     dp.register_message_handler(send_state_media_group, lambda message: message.text == "Получить медиа", state=Attachments_temp_state.ADDITION)
