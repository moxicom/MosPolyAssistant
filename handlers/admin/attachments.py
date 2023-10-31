import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import ParseMode
from aiogram.contrib.middlewares.logging import LoggingMiddleware

logging.basicConfig(level=logging.INFO)

#-----------------------------------------------------------------------
# This is a test additional file for attachments fumctions in messages.
#-----------------------------------------------------------------------

bot = Bot(token='') # Bot token for test

dp = Dispatcher(bot)

dp.middleware.setup(LoggingMiddleware())

user_id_to_send = '' # For test, enter chat_id

async def on_start(message: types.Message):
    await message.answer("Привет! Отправьте мне файл, и я перешлю его Никите.")

# Only for documents(some extentions of custom files)
async def on_document_received(message: types.Message):

    document = message.document # Get all info about attachment
    
    # To register file to DB, call func and argument to it "document.file_id"
    await insert_attachment(file=document.file_id)

    try:
        # To send file to some user/users call func "send_document", argument to it "User ID" and "File ID"
        await bot.send_document(chat_id=user_id_to_send, document=document.file_id)
        await message.answer("Файл успешно отправлен.")
    except Exception as e:
        await message.answer(f"Произошла ошибка: {e}")

# Only for compressed photos
async def on_photo_received(message: types.Message):

    photo = message.photo[-1] 
    
    await insert_attachment(image=photo.file_id)

    try:
        await bot.send_photo(chat_id=user_id_to_send, photo=photo.file_id)
        await message.answer("Фото успешно отправлено.")
    except Exception as e:
        await message.answer(f"Произошла ошибка: {e}")

# Only for compressed videos
async def on_video_received(message: types.Message):

    video = message.video

    await insert_attachment(video=video.file_id)

    try:
        await bot.send_video(chat_id=user_id_to_send, video=video.file_id)
        await message.answer("Видео успешно отправлено.")
    except Exception as e:
        await message.answer(f"Произошла ошибка: {e}")

# Only for audio FILES
async def on_audio_received(message: types.Message):

    audio = message.audio

    await insert_attachment(audio=audio.file_id)

    try:
        await bot.send_audio(chat_id=user_id_to_send, audio=audio.file_id)
        await message.answer("Аудиофайл успешно отправлен.")
    except Exception as e:
        await message.answer(f"Произошла ошибка: {e}")

def attachments_handlers(dp: Dispatcher):
    dp.register_message_handler(on_start, commands=['start'])
    dp.register_message_handler(on_document_received, content_types=types.ContentType.DOCUMENT)
    dp.register_message_handler(on_photo_received, content_types=types.ContentType.PHOTO)
    dp.register_message_handler(on_video_received, content_types=types.ContentType.VIDEO)
    dp.register_message_handler(on_audio_received, content_types=types.ContentType.AUDIO)

if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)

