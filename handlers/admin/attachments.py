import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import ParseMode, InputMediaPhoto, ReplyKeyboardMarkup, KeyboardButton, InputMediaDocument, InputMediaVideo
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import ContentTypeFilter

#
from aiogram.dispatcher.handler import CancelHandler
from typing import List, Union
from aiogram.dispatcher.middlewares import BaseMiddleware
#

from Db import db_attachmments

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


async def update_media_group(user_id_to_send_info: int, message: types.Message, state: FSMContext):
    current_state = await state.get_data()
    media_input = current_state.get("media_input") or MediaInput()
    try:
        if message.photo:
            photo_id = message.photo[-1].file_id
            media_input.photos.append(photo_id)

        elif message.document:
            print("document: ", message.document.file_id)
            media_input.documents.append(message.document.file_id)

        elif message.video:
            for video in message.video:
                media_input.videos.append(message.video.file_id)
        print('media_input docs', media_input.documents )
        await state.update_data(media_input=media_input)
        

    except Exception as e:
        logging.warning(f'|attachments/make_media_group| An error has occurred: {e}')
        await state.finish()
    return


async def get_media_group(user_id_to_send: int, user_id_to_send_info: int, state: FSMContext) -> list:
    media = []
    try:
        async with state.proxy() as data:
            media_group : MediaInput = data['media_input']
            photos = media_group.photos
            documents = media_group.documents
            videos = media_group.videos
            print('photos', photos)
            print('documents', documents)
            print('videos', videos)
        for photo in photos:
            media.append(InputMediaPhoto(media=photo))
        for document_id in documents:
            media.append(InputMediaDocument(media=document_id))
        for video_id in videos:
            media.append(InputMediaVideo(media=video_id))
    except Exception as e:
        logging.warning(f'|attachments/get_media_group| An error has occurred: {e}')
        await state.finish()
    return media


async def receive_message_with_media(message: types.Message, state: FSMContext):
    await update_media_group(user_id_to_send_info=message.from_user.id, message=message, state=state)
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("Получить изображения"))
    await message.answer("Медиа загружено", reply_markup = keyboard)
    

async def send_message(message: types.Message, state: FSMContext):
    logging.info("sending message...")
    media = await get_media_group(message.from_user.id, message.from_user.id, state)
    print("media", set(media))
    await bot.send_media_group(message.chat.id, media)


def temp_attachments_handler(dp: Dispatcher):
    dp.register_message_handler(temp_start, commands=['attachments'], state='*')
    dp.register_message_handler(receive_message_with_media, state=Attachments_temp_state.ADDITION, content_types=[
    types.ContentType.PHOTO,
    types.ContentType.VIDEO,
    types.ContentType.DOCUMENT,
    types.ContentType.AUDIO,
    ])

    dp.register_message_handler(send_message, lambda message: message.text == "Получить изображения", state=Attachments_temp_state.ADDITION)
