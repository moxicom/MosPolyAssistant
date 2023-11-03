import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import ParseMode
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import ContentTypeFilter

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



# /// ONE MEDIA PER ONE MESSAGE HANDLERS ///

# Мы с одним файлом работаем?? так же неправильно, надо исправлять
# async def make_media_group(user_id_to_send: int, video_id=None, file_id=None, image_id=None, audio_id=None) -> list:
#     '''Command handler for sending attachments to user with send exceptions handling'''
#     media_group = []
#     try:
#         if video_id:
#             media_group.append(types.InputMediaVideo(video_id)) # Это что за пиздец, надо проверить, работает ли это
#         if file_id:
#             media_group.append(types.InputMediaDocument(file_id))
#         if image_id:
#             media_group.append(types.InputMediaPhoto(image_id))
#         if audio_id:
#             media_group.append(types.InputMediaAudio(audio_id))
#     except Exception as e:
#         logging.warning(f'|attachments/make_media| An error has occurred: {e}')
#         return []
#     return media_group

# Only for documents(some extentions of custom files)
async def on_document_received(message: types.Message, state: FSMContext):
    document = message.document
    await state.update_data(document_id=document.file_id)


# Only for compressed photos
async def on_photo_received(message: types.Message, state: FSMContext):
    photo = message.photo[-1]
    await state.update_data(image_id=photo.file_id)


# Only for compressed videos
async def on_video_received(message: types.Message, state: FSMContext):
    video = message.video
    await state.update_data(video=video.file_id)


# Only for audio FILES
async def on_audio_received(message: types.Message, state: FSMContext):
    audio = message.audio
    await state.update_data(audio=audio.file_id)



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
    # for photo in message.photo:
    #     photo_id = photo.file_unique_id
    #     print(photo_id)
    #     # await bot.send_photo(message.chat.id, photo_id)
    
async def send_message(message: types.Message, state: FSMContext):
    media = await get_media_group(message.from_user.id, message.from_user.id, state)
    await bot.send_media_group(message.chat.id, media)


def temp_attachments_handler(dp: Dispatcher):
    dp.register_message_handler(temp_start, commands=['attachments'], state='*')
    dp.register_message_handler(receive_message, state=Attachments_temp_state.ADDITION, content_types=[
    types.ContentType.PHOTO,
    types.ContentType.VIDEO,
    types.ContentType.DOCUMENT,
    types.ContentType.AUDIO
    ])
    dp.message_handler(send_message, state=Attachments_temp_state.ADDITION)
