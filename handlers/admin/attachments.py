import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import ParseMode, InputMediaPhoto
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


async def send_message_template(state:FSMContext, user_id_to_send: int, user_id_to_send_info:int, message: str, media_group: list = [], reply_markup: types.InlineKeyboardMarkup = None) -> bool:
    '''Command handler for sending attachments to user with send exceptions handling'''
    try:
        pass
    except Exception as e:
        logging.warning(f'|attachments/send_message_template| An error has occurred: {e}')
        await state.finish()
        return False
    return True

# /// MULTIPLE MEDIA PER ONE MESSAGE HANDLERS ///
class MediaInput:
    def __init__(self):
        self.photos = []
        self.documents = []
        self.videos = []


async def make_media_group(user_id_to_send: int, user_id_to_send_info: int, message: types.Message, state: FSMContext):
    media_input = MediaInput()
    print("make_media_group : photos: ", message.photo)
    try:
        if message.photo:
            photo_id = message.photo[-1].file_id
            media_input.photos.append(photo_id)

        if message.document:
            for document in message.document:
                media_input.documents.append(message.document.file_id)

        if message.video:
            for video in message.video:
                media_input.videos.append(message.video.file_id)

        async with state.proxy() as data:
            media_input_state = data.get('media_input')
            media_input_state.photos.extend(media_input.photos)
            media_input_state.photos = list(set(media_input.photos))
            data["media_input"] = media_input_state
            

    except Exception as e:
        logging.warning(f'|attachments/make_media_group| An error has occurred: {e}')
        await state.finish()
    return


async def get_media_group(user_id_to_send: int, user_id_to_send_info: int, state: FSMContext) -> list:
    media = []
    try:
        async with state.proxy() as data:
            photos = data['media_input'].photos
            documents = data['media_input'].documents
            videos = data['media_input'].videos
        print("get_media_group : photos: ", photos)
        for photo in photos:
            media.append(types.InputMediaPhoto(media=photo))
        for document_id in documents:
            media.append(types.InputMediaDocument(media=document_id))
        for video_id in videos:
            media.append(types.InputMediaVideo(media=video_id))
    except Exception as e:
        logging.warning(f'|attachments/get_media_group| An error has occurred: {e}')
        await state.finish()
    return media


async def receive_message(message: types.Message, state: FSMContext):
    await make_media_group(message.from_user.id, message.from_user.id, message, state)
    await state.finish()
    # photo_id = message.photo[-1].file_id
    # await bot.send_photo(message.chat.id, photo_id) 
    
async def send_message(message: types.Message, state: FSMContext):
    media = await get_media_group(message.from_user.id, message.from_user.id, state)
    await bot.send_media_group(message.chat.id, media)


class AlbumMiddleware(BaseMiddleware):
    """This middleware is for capturing media groups."""

    album_data: dict = {}

    def __init__(self, latency: Union[int, float] = 0.01):
        """
        You can provide custom latency to make sure
        albums are handled properly in highload.
        """
        self.latency = latency
        super().__init__()

    async def on_process_message(self, message: types.Message, data: dict):
        if not message.media_group_id:
            return

        try:
            self.album_data[message.media_group_id].append(message)
            raise CancelHandler()  # Tell aiogram to cancel handler for this group element
        except KeyError:
            self.album_data[message.media_group_id] = [message]
            # await asyncio.sleep(self.latency)
            message.conf["is_last"] = True
            data["album"] = self.album_data[message.media_group_id]

    async def on_post_process_message(self, message: types.Message, result: dict, data: dict):
        """Clean up after handling our album."""
        if message.media_group_id and message.conf.get("is_last"):
            del self.album_data[message.media_group_id]


async def handle_albums(message: types.Message):
    """This handler will receive a complete album of any type."""
    media_group = types.MediaGroup()
    for obj in album:
        if obj.photo:
            file_id = obj.photo[-1].file_id
        else:
            file_id = obj[obj.content_type].file_id

        try:
            # We can also add a caption to each file by specifying `"caption": "text"`
            media_group.attach({"media": file_id, "type": obj.content_type})
        except ValueError:
            return await message.answer("This type of album is not supported by aiogram.")

    await message.answer_media_group(media_group)


def temp_attachments_handler(dp: Dispatcher):
    # dp.middleware.setup(AlbumMiddleware())
    dp.register_message_handler(temp_start, commands=['attachments'], state='*')
    # dp.register_message_handler(receive_message, state=Attachments_temp_state.ADDITION, content_types=[
    # types.ContentType.PHOTO,
    # types.ContentType.VIDEO,
    # types.ContentType.DOCUMENT,
    # types.ContentType.AUDIO
    # ])
    # dp.message_handler(send_message, state=Attachments_temp_state.ADDITION)
    dp.register_message_handler(handle_albums, content_types=types.ContentType.ANY)
