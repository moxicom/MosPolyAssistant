
from aiogram import Dispatcher, types
from Db import db_client as db_client
from config import bot

async def send_message(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    message_id = int(callback_query.data.split(":")[1])
    msg = await db_client.fetch_message_by_id(message_id)
    if msg: 
        await bot.send_message(callback_query.from_user.id, f"Заголовок: {msg.title}\nТекст: {msg.text}")
    else:
         await bot.send_message(callback_query.from_user.id, "Данное сообщение предназначено для другой группы.")  

def messages_system_handler(dp: Dispatcher):
    dp.register_callback_query_handler(send_message, lambda c: c.data.startswith("receive_message_by_id"), state="*")